from django.urls import path
from . import views

app_name = 'recipes'
 
urlpatterns = [
    path('recipes/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('r/<int:pk>/', views.short_recipe_redirect, name='short_recipe_redirect'),
] 