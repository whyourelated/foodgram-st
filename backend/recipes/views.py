from django.http import HttpResponseRedirect

def short_recipe_redirect(request, pk):
    return HttpResponseRedirect(f'/recipes/{pk}/') 