from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from accounts.models import Follow
from .models import Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingList

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'recipes_count', 'followers_count', 'following_count')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'date_joined')

    @admin.display(description='Рецепты')
    def recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description='Подписчики')
    def followers_count(self, obj):
        return obj.followers.count()

    @admin.display(description='Подписки')
    def following_count(self, obj):
        return obj.following.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)

    @admin.display(description='Рецепты')
    def recipes_count(self, obj):
        return obj.recipes.count()


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cooking_time', 'author',
                    'favorites_count', 'ingredients_list', 'image_preview')
    search_fields = ('name', 'author__username')
    list_filter = ('author',)
    inlines = (RecipeIngredientInline,)

    @admin.display(description='Ингредиенты')
    def ingredients_list(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj).select_related('ingredient')
        return mark_safe('<br>'.join(
            f'{ri.ingredient.name} ({ri.ingredient.measurement_unit}) — {ri.amount}'
            for ri in ingredients
        ))

    @admin.display(description='Изображение')
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return 'Нет изображения'

    @admin.display(description='В избранном')
    def favorites_count(self, obj):
        return obj.favorites.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
