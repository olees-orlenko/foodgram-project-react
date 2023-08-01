from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import exceptions, filters, status, viewsets

from recipe.models import (Ingredients,
                           Recipe,
                           RecipeIngredients,
                           ShoppingList,
                           Subscription,
                           Tag,
                           User)
from api.filters import SlugFilter
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (FavoritesList,
                             IngredientsSerializer,
                             RecipeCreateSerializer,
                             RecipeFavoriteSerializer,
                             RecipeSerializer,
                             SetPasswordSerializer,
                             SubscribeSerializer,
                             SubscriptionSerializer,
                             TagSerializer,
                             UserCreateSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend,)
    pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny,)
    serializer_class = UserCreateSerializer

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserCreateSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = SetPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Пароль изменен'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        paginate_queryset = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(paginate_queryset, many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=request.user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            get_object_or_404(Subscription, user=request.user,
                              author=author).delete()
            return Response({'detail': 'Успешная отписка'},
                            status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SlugFilter
    filterset_fields = ('author', 'tag')
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    serializer_class = RecipeSerializer

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipeingredients__ingredients', 'tag'
            ).all()
        return recipes

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, **kwargs):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            if FavoritesList.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise exceptions.ValidationError(
                    'Рецепт уже добавен в избранное.'
                    )
            favoriteslist = FavoritesList.objects.create(user=user)
            favoriteslist.recipe.set([recipe])
            serializer = RecipeFavoriteSerializer(
                recipe,
                context={'request': request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            favoriteslist = get_object_or_404(
                FavoritesList,
                user=user,
                recipe=recipe)
            favoriteslist.delete()
            return Response({'detail': 'Рецепт удален.'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = self.request.user
        if request.method == 'POST':
            shoppinglist_recipe, created = ShoppingList.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            if not created:
                raise exceptions.ValidationError(
                    'Рецепт уже в списке покупок.'
                    )
            serializer = RecipeSerializer(
                recipe,
                context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            get_object_or_404(ShoppingList, user=user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт успешно удален из списка покупок.'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingList.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        recipeingredients_list = RecipeIngredients.objects.filter(
            recipe__in=recipes).values('ingredients').annotate(
            amount=Sum('amount'))
        text = 'Список покупок:\n\n'
        for item in recipeingredients_list:
            ingredient = Ingredients.objects.get(pk=item['ingredients'])
            amount = item['amount']
            text += (f'{ingredient.name}, {amount} '
                     f'{ingredient.measurement_units}\n'
                     )
        response = HttpResponse(text, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=shopping_cart.txt')
        return response


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name', )
    permission_classes = (AllowAny,)
    serializer_class = IngredientsSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
