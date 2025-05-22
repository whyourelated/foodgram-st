from django.contrib import admin
from django.utils.safestring import mark_safe
from django.db.models import Count, Avg
from django.contrib.auth import get_user_model
from .models import Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingList, User, Follow

User = get_user_model()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 
                   'recipes_count', 'followers_count', 'following_count')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'date_joined')

    def recipes_count(self, user):
        return user.recipes.count()
    recipes_count.short_description = 'Количество рецептов'

    def followers_count(self, user):
        return user.followers.count()
    followers_count.short_description = 'Подписчики'

    def following_count(self, user):
        return user.following.count()
    following_count.short_description = 'Подписки'

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit', 'recipes__isnull')

    def recipes_count(self, ingredient):
        return ingredient.recipes.count()
    recipes_count.short_description = 'Количество рецептов'


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cooking_time', 'author', 
                   'favorites_count', 'ingredients_list', 'image_preview')
    search_fields = ('name', 'author__username')
    list_filter = ('author', 'cooking_time')
    inlines = (RecipeIngredientInline,)

    def get_list_filter(self, request):
        filters = super().get_list_filter(request)
        # Calculate cooking time thresholds based on current data
        avg_time = Recipe.objects.aggregate(avg=Avg('cooking_time'))['avg']
        if avg_time:
            quick_threshold = int(avg_time * 0.7)  # 70% of average
            slow_threshold = int(avg_time * 1.3)   # 130% of average
            
            # Get counts for each category
            quick_count = Recipe.objects.filter(cooking_time__lte=quick_threshold).count()
            medium_count = Recipe.objects.filter(
                cooking_time__gt=quick_threshold,
                cooking_time__lte=slow_threshold
            ).count()
            slow_count = Recipe.objects.filter(cooking_time__gt=slow_threshold).count()
            
            # Replace the cooking_time filter with our custom one
            filters = list(filters)
            time_index = filters.index('cooking_time')
            filters[time_index] = (
                'cooking_time',
                {
                    'title': 'Время приготовления',
                    'parameter_name': 'cooking_time',
                    'lookups': (
                        ('lte', f'Быстрее {quick_threshold} мин ({quick_count})'),
                        ('gt', f'Дольше {slow_threshold} мин ({slow_count})'),
                        ('range', f'От {quick_threshold} до {slow_threshold} мин ({medium_count})'),
                    ),
                }
            )
        return filters

    @mark_safe
    def ingredients_list(self, recipe):
        ingredients = recipe.ingredients.all()
        return '<br>'.join(
            f'{ing.name} ({ing.measurement_unit})'
            for ing in ingredients
        )
    ingredients_list.short_description = 'Ингредиенты'

    @mark_safe
    def image_preview(self, recipe):
        if recipe.image:
            return f'<img src="{recipe.image.url}" width="50" height="50" />'
        return 'Нет изображения'
    image_preview.short_description = 'Изображение'

    def favorites_count(self, recipe):
        return recipe.favorites.count()
    favorites_count.short_description = 'В избранном'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name') 