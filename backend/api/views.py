from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (
    Product, Dish, DishProduct, Bookmark, ShoppingList
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

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        dish = self.get_object()
        if request.method == 'POST':
            if Bookmark.objects.filter(user=request.user, dish=dish).exists():
                return Response(
                    {'error': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Bookmark.objects.create(user=request.user, dish=dish)
            serializer = BookmarkSerializer(
                Bookmark.objects.get(user=request.user, dish=dish)
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        bookmark = get_object_or_404(Bookmark, user=request.user, dish=dish)
        bookmark.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        dish = self.get_object()
        if request.method == 'POST':
            if ShoppingList.objects.filter(user=request.user, dish=dish).exists():
                return Response(
                    {'error': 'Рецепт уже в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingList.objects.create(user=request.user, dish=dish)
            serializer = ShoppingListSerializer(
                ShoppingList.objects.get(user=request.user, dish=dish)
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        shopping_item = get_object_or_404(
            ShoppingList, user=request.user, dish=dish
        )
        shopping_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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

    @action(detail=False, methods=['get'])
    def download(self, request):
        user = request.user
        shopping_items = {}
        for item in ShoppingList.objects.filter(user=user):
            for dp in DishProduct.objects.filter(dish=item.dish):
                name = dp.product.name
                unit = dp.product.unit
                amount = dp.amount
                key = (name, unit)
                shopping_items[key] = shopping_items.get(key, 0) + amount

        lines = [
            f'{name} ({unit}) — {amount}'
            for (name, unit), amount in shopping_items.items()
        ]
        content = '\n'.join(lines)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response


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