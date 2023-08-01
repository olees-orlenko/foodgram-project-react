from django.contrib import admin

from recipe.models import (FavoritesList,
                           Ingredients,
                           Recipe,
                           RecipeIngredients,
                           ShoppingList,
                           Subscription,
                           Tag,
                           User)


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientsInline, )
    list_display = (
        'pk',
        'name',
        'author',
        'text',
        'cooking_time',
        'in_favorites_list'
    )
    list_editable = ('name', 'cooking_time', 'text', 'author')
    search_fields = ('name', 'author')
    list_filter = ('name', 'author', 'tag')
    empty_value_display = '-пусто-'

    @admin.display(description='Избранное')
    def in_favorites_list(self, obj):
        return obj.favoriteslist.count()


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'colour', 'slug')


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_units')
    list_filter = ('name', )
    search_fields = ('name', )


class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredients', 'amount')


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')


class FavoritesListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'get_favorite_recipe')

    @admin.display(description='Любимые рецепты')
    def get_favorite_recipe(self, obj):
        return [
            f'{item["name"]} ' for item in obj.recipe.values('name')[:5]]


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(RecipeIngredients, RecipeIngredientsAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(FavoritesList, FavoritesListAdmin)
