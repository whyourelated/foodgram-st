from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (
    Product, Dish, DishProduct, Bookmark, ShoppingList, Subscription
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from .filters import DishFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    ProductSerializer, DishSerializer, DishProductSerializer,
    BookmarkSerializer, ShoppingListSerializer, CustomUserSerializer
)

User = get_user_model()

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для продуктов (ингредиентов)."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    search_fields = ('name',)


class DishViewSet(viewsets.ModelViewSet):
    """Вьюсет для блюд (рецептов)."""
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = DishFilter

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def add_obj(self, model, user, dish, serializer_class):
        if model.objects.filter(user=user, dish=dish).exists():
            return Response(
                {'error': 'Рецепт уже добавлен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=user, dish=dish)
        serializer = serializer_class(dish)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_obj(self, model, user, dish):
        obj = model.objects.filter(user=user, dish=dish)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Рецепта нет в списке'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        dish = self.get_object()
        if request.method == 'POST':
            return self.add_obj(Bookmark, request.user, dish, DishSerializer)
        return self.delete_obj(Bookmark, request.user, dish)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        dish = self.get_object()
        if request.method == 'POST':
            return self.add_obj(ShoppingList, request.user, dish, DishSerializer)
        return self.delete_obj(ShoppingList, request.user, dish)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_items = {}
        for item in ShoppingList.objects.filter(user=user):
            for dp in DishProduct.objects.filter(dish=item.dish):
                name = dp.product.name
                unit = dp.product.unit
                amount = dp.amount
                key = (name, unit)
                shopping_items[key] = shopping_items.get(key, 0) + amount

        format_type = request.query_params.get('format', 'pdf')
        if format_type == 'txt':
            lines = [
                f'{i+1}. {name} ({unit}) — {amount}'
                for i, ((name, unit), amount) in enumerate(shopping_items.items())
            ]
            content = 'Список ингредиентов:\n\n' + '\n'.join(lines)
            response = HttpResponse(content, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
            return response

        # PDF export
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen import canvas
        import os
        font_path = os.path.join(os.path.dirname(__file__), '../Slimamif.ttf')
        pdfmetrics.registerFont(TTFont('Slimamif', font_path, 'UTF-8'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.pdf"'
        page = canvas.Canvas(response)
        page.setFont('Slimamif', size=24)
        page.drawString(200, 800, 'Список ингредиентов')
        page.setFont('Slimamif', size=16)
        height = 750
        for i, ((name, unit), amount) in enumerate(shopping_items.items(), 1):
            page.drawString(75, height, f'{i}. {name} — {amount} {unit}')
            height -= 25
        page.showPage()
        page.save()
        return response


class BookmarkViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для избранных рецептов."""
    serializer_class = DishSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Dish.objects.filter(bookmarks__user=self.request.user)


class ShoppingListViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для списка покупок."""
    serializer_class = DishSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Dish.objects.filter(shopping_lists__user=self.request.user)


class CustomUserViewSet(UserViewSet):
    """Расширенный вьюсет пользователя."""
    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if user == author:
                return Response(
                    {'error': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user.subscriptions.filter(author=author).exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.subscriptions.create(author=author)
            return Response(status=status.HTTP_201_CREATED)

        subscription = get_object_or_404(
            user.subscriptions, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = Subscription.objects.filter(subscriber=user)
        authors = [sub.author for sub in subscriptions]
        page = self.paginate_queryset(authors)
        serializer = CustomUserSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data) 