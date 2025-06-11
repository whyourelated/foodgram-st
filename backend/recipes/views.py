from django.http import Http404
from django.shortcuts import redirect
from .models import Recipe

def short_recipe_redirect(request, pk):
    try:
        recipe = Recipe.objects.get(pk=pk)
    except Recipe.DoesNotExist:
        raise Http404(f'Рецепт с id {pk} не найден.')
    
    return redirect(f'/recipes/{pk}/')