from django_filters import rest_framework as filters

from recipe.models import Recipe, Tag, User


class SlugFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tag = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                            to_field_name='slug',
                                            queryset=Tag.objects.all())
    is_favorited = filters.BooleanFilter(method='get_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_shopping_cart_filter'
        )

    class Meta:
        model = Recipe
        fields = ('author', 'tag', 'is_favorited', 'is_in_shopping_cart')

    def get_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favoriteslist_recipe__user=user)
        return queryset

    def get_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shoppinglist_recipe__user=user)
        return queryset
