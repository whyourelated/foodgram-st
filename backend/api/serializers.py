from rest_framework import serializers
from recipes.models import Product, Dish, DishProduct, Bookmark, ShoppingList
from accounts.models import Subscription
from django.contrib.auth import get_user_model

User = get_user_model()

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'unit')

class DishProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = DishProduct
        fields = ('id', 'product', 'product_id', 'amount')

class DishSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField(read_only=True)
    products = DishProductSerializer(source='dishproduct_set', many=True, read_only=True)
    image = serializers.ImageField()

    class Meta:
        model = Dish
        fields = (
            'id', 'creator', 'title', 'image', 'description',
            'products', 'cook_time'
        )

class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ('id', 'user', 'dish')

class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ('id', 'user', 'dish')

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('id', 'subscriber', 'author') 