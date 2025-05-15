from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Product(models.Model):  # Ingredient
    name = models.CharField(max_length=200, verbose_name='Название')
    unit = models.CharField(max_length=50, verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.unit})'


class Dish(models.Model):  # Recipe
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe_creators',
        verbose_name='Создатель'
    )
    title = models.CharField(max_length=200, verbose_name='Название')
    image = models.ImageField(upload_to='dishes/', verbose_name='Картинка')
    description = models.TextField(verbose_name='Описание')
    products = models.ManyToManyField(
        Product, through='DishProduct', verbose_name='Ингредиенты'
    )
    cook_time = models.PositiveIntegerField(verbose_name='Время приготовления (мин)')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'
        ordering = ['-pub_date']

    def __str__(self):
        return self.title


class DishProduct(models.Model):  # RecipeIngredient
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингредиент блюда'
        verbose_name_plural = 'Ингредиенты блюда'
        unique_together = ('dish', 'product')


class Bookmark(models.Model):  # Favorite
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bookmarks', verbose_name='Пользователь'
    )
    dish = models.ForeignKey(
        Dish, on_delete=models.CASCADE, related_name='in_bookmarks', verbose_name='Блюдо'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ('user', 'dish')

    def __str__(self):
        return f'{self.user} добавил {self.dish} в избранное'


class ShoppingList(models.Model):  # ShoppingCart
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_lists', verbose_name='Пользователь'
    )
    dish = models.ForeignKey(
        Dish, on_delete=models.CASCADE, related_name='in_shopping_lists', verbose_name='Блюдо'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        unique_together = ('user', 'dish')

    def __str__(self):
        return f'{self.user} добавил {self.dish} в список покупок' 