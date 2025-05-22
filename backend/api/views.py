from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (
    Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingList
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from datetime import datetime

from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer, RecipeSerializer, UserSerializer
)

User = get_user_model()

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_to_favorites(self, user, recipe):
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError('Рецепт уже добавлен в избранное')
        Favorite.objects.create(user=user, recipe=recipe)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_from_favorites(self, user, recipe):
        favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def add_to_shopping_cart(self, user, recipe):
        if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError('Рецепт уже добавлен в список покупок')
        ShoppingList.objects.create(user=user, recipe=recipe)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_from_shopping_cart(self, user, recipe):
        shopping_item = get_object_or_404(ShoppingList, user=user, recipe=recipe)
        shopping_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            return self.add_to_favorites(request.user, recipe)
        return self.remove_from_favorites(request.user, recipe)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            return self.add_to_shopping_cart(request.user, recipe)
        return self.remove_from_shopping_cart(request.user, recipe)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_items = {}
        recipes_info = {}

        for item in user.shopping_list.all():
            recipe = item.recipe
            recipes_info[recipe.id] = f'{recipe.name} ({recipe.author.get_full_name()})'
            
            for ingredient in recipe.ingredients.all():
                amount = RecipeIngredient.objects.get(
                    recipe=recipe, ingredient=ingredient
                ).amount
                key = (ingredient.name.capitalize(), ingredient.measurement_unit)
                shopping_items[key] = shopping_items.get(key, 0) + amount

        current_date = datetime.now().strftime('%d.%m.%Y')
        content = [
            f'Список покупок на {current_date}\n',
            'Рецепты:',
            *[f'- {info}' for info in recipes_info.values()],
            '\nИнгредиенты:',
            *[f'{i}. {name} ({unit}) — {amount}'
              for i, ((name, unit), amount) in enumerate(
                  sorted(shopping_items.items()), 1
              )]
        ]

        response = FileResponse(
            '\n'.join(content).encode('utf-8'),
            as_attachment=True,
            filename='shopping_list.txt'
        )
        return response


class UserViewSet(UserViewSet):
    """Вьюсет пользователя."""
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
                raise ValidationError('Нельзя подписаться на самого себя')
            if user.follower.filter(author=author).exists():
                raise ValidationError(f'Вы уже подписаны на {author.get_full_name()}')
            user.follower.create(author=author)
            return Response(status=status.HTTP_201_CREATED)

        subscription = get_object_or_404(user.follower, author=author)
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
        authors = User.objects.filter(following__user=user)
        page = self.paginate_queryset(authors)
        serializer = UserSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data) 