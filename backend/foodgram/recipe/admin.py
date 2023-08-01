from django.contrib import admin
from django.core.exceptions import ValidationError

from recipe.models import (FavoritesList, Ingredients, Recipe,
                           RecipeIngredients, ShoppingList, Subscription, Tags)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 1

    def save_model(self, request, obj, form, change):
        if not obj.ingredients.exists() or not obj.tags.exists():
            raise ValidationError(
                "Добавьте в рецепт ингредиенты и тэг"
            )
        super().save_model(request, obj, form, change)


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientsInline, )
    list_display = (
        'pk',
        'name',
        'author',
        'text',
        'cooking_time',
        'in_favorites_list',
        '_ingredients'
    )
    list_editable = ('name',
                     'cooking_time',
                     'text',
                     'author')
    search_fields = ('name', 'author', '_ingredients')
    list_filter = ('name', 'author', 'tags', 'ingredients')
    empty_value_display = '-пусто-'

    @admin.display(description='Избранное')
    def in_favorites_list(self, obj):
        return obj.favoriteslist.count()

    def _ingredients(self, row):
        return ', '.join([x.name for x in row.ingredients.all()])

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        form.save_m2m()
        if not form.cleaned_data.get('ingredients'):
            super().save_model(request, obj, form, change)


class TagsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_units')
    list_filter = ('name', )
    search_fields = ('name', )


class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredients', 'amount')


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')


class FavoritesListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user')


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(RecipeIngredients, RecipeIngredientsAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(FavoritesList, FavoritesListAdmin)
