from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingList
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from datetime import datetime

from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import IngredientSerializer, RecipeReadSerializer, RecipeWriteSerializer, UserSerializer

User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _handle_add_relation(self, user, recipe, model, error_msg):
        obj, created = model.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            raise ValidationError(error_msg)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _handle_remove_relation(self, user, recipe, model):
        model.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            return self._handle_add_relation(
                request.user, recipe, Favorite, 'Рецепт уже в избранном'
            )
        return self._handle_remove_relation(request.user, recipe, Favorite)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            return self._handle_add_relation(
                request.user, recipe, ShoppingList, 'Рецепт уже в списке покупок'
            )
        return self._handle_remove_relation(request.user, recipe, ShoppingList)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        user = request.user
        shopping_items = {}

        for item in user.shopping_list.select_related('recipe__author').all():
            recipe = item.recipe
            ingredients = RecipeIngredient.objects.filter(recipe=recipe).select_related('ingredient')
            for ri in ingredients:
                key = (ri.ingredient.name.title(), ri.ingredient.measurement_unit)
                shopping_items[key] = shopping_items.get(key, 0) + ri.amount

        current_date = datetime.now().strftime('%d.%m.%Y')
        content = [
            f'Список покупок на {current_date}',
            '',
            'Ингредиенты:',
            *[f'{i}. {name} ({unit}) — {amount}'
              for i, ((name, unit), amount) in enumerate(
                  sorted(shopping_items.items()), 1
              )]
        ]
        return FileResponse(
            '\n'.join(content),
            as_attachment=True,
            filename='shopping_list.txt'
        )

class UserViewSet(DjoserUserViewSet):
    """Вьюсет пользователя."""

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            raise ValidationError('Нельзя подписаться на самого себя')
        if request.method == 'POST':
            _, created = user.follower.get_or_create(author=author)
            if not created:
                raise ValidationError('Вы уже подписаны на этого автора')
            return Response(status=status.HTTP_201_CREATED)

        get_object_or_404(user.follower, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='subscriptions')
    def subscriptions(self, request):
        user = request.user
        authors = User.objects.filter(following__user=user)
        page = self.paginate_queryset(authors)
        serializer = UserSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data) 
