from django.contrib import admin
from django.urls import path, include
from recipes.views import short_recipe_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('r/<int:pk>/', short_recipe_redirect, name='short_recipe_redirect'),
] 