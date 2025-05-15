from django.contrib import admin
from .models import Product, Dish, DishProduct, Bookmark, ShoppingList

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit')
    search_fields = ('name',)

class DishProductInline(admin.TabularInline):
    model = DishProduct
    extra = 1

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'favorites_count')
    search_fields = ('title', 'creator__username')
    inlines = (DishProductInline,)

    def favorites_count(self, obj):
        return obj.bookmarks.count()
    favorites_count.short_description = 'В избранном'

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'dish')
    search_fields = ('user__username', 'dish__title')

@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'dish')
    search_fields = ('user__username', 'dish__title') 