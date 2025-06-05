from django.http import Http404
from django.shortcuts import redirect
from .models import Recipe

def short_recipe_redirect(request, pk):
    if not Recipe.objects.filter(pk=pk).exists():
        raise Http404('Рецепт не найден.')
    return redirect('recipes:recipe_detail', recipe_id=pk)
