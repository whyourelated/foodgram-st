from django.urls import path
from . import views

app_name = 'recipes'
 
urlpatterns = [
    path('r/<int:pk>/', views.short_recipe_redirect, name='short_recipe_redirect'),
] 