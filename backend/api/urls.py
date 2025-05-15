from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ProductViewSet, DishViewSet, BookmarkViewSet,
    ShoppingListViewSet, CustomUserViewSet
)

app_name = 'api'

router = DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('ingredients', ProductViewSet)
router.register('recipes', DishViewSet)
router.register('favorites', BookmarkViewSet, basename='favorites')
router.register('shopping_cart', ShoppingListViewSet, basename='shopping_cart')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
] 