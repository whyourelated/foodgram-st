import json
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from recipes.models import Product, Dish, DishProduct

User = get_user_model()

class Command(BaseCommand):
    help = 'Load test data'

    def handle(self, *args, **options):
        # Создаем суперпользователя
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin'
            )

        # Создаем тестовых пользователей
        test_users = [
            {
                'username': 'test_user1',
                'email': 'test1@example.com',
                'password': 'testpass123'
            },
            {
                'username': 'test_user2',
                'email': 'test2@example.com',
                'password': 'testpass123'
            }
        ]

        for user_data in test_users:
            if not User.objects.filter(username=user_data['username']).exists():
                User.objects.create_user(**user_data)

        # Загружаем ингредиенты из JSON
        with open('data/ingredients.json', 'r', encoding='utf-8') as f:
            ingredients = json.load(f)
            for ingredient in ingredients:
                Product.objects.get_or_create(
                    name=ingredient['name'],
                    unit=ingredient['measurement_unit']
                )

        # Создаем тестовые рецепты
        test_recipes = [
            {
                'title': 'Паста Карбонара',
                'description': 'Классическая итальянская паста',
                'cook_time': 30,
                'ingredients': [
                    {'name': 'Спагетти', 'amount': 200, 'unit': 'г'},
                    {'name': 'Бекон', 'amount': 100, 'unit': 'г'},
                    {'name': 'Сливки', 'amount': 100, 'unit': 'мл'}
                ]
            },
            {
                'title': 'Салат Цезарь',
                'description': 'Классический салат с курицей',
                'cook_time': 20,
                'ingredients': [
                    {'name': 'Куриная грудка', 'amount': 200, 'unit': 'г'},
                    {'name': 'Салат Айсберг', 'amount': 1, 'unit': 'шт'},
                    {'name': 'Сухарики', 'amount': 50, 'unit': 'г'}
                ]
            }
        ]

        for recipe_data in test_recipes:
            dish = Dish.objects.create(
                creator=User.objects.get(username='test_user1'),
                title=recipe_data['title'],
                description=recipe_data['description'],
                cook_time=recipe_data['cook_time']
            )
            
            for ingredient in recipe_data['ingredients']:
                product = Product.objects.get(name=ingredient['name'])
                DishProduct.objects.create(
                    dish=dish,
                    product=product,
                    amount=ingredient['amount']
                ) 