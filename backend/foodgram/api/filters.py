from django_filters import rest_framework as filters

from recipe.models import Recipe, Tags


class SlugFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tags.objects.all())
    is_favorited = filters.BooleanFilter(method='get_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_shopping_cart_filter')

    def get_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favoriteslist__user=user)
        return queryset

    def get_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shoppinglist__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
