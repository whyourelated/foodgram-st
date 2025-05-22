from django.shortcuts import get_object_or_404, redirect
from .models import Recipe

def short_recipe_redirect(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return redirect('recipes:recipe_detail', recipe_id=recipe.id) 