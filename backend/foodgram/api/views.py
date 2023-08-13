from api.filters import SlugFilter
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (FavoritesList, IngredientsSerializer,
                             RecipeCreateSerializer, RecipeFavoriteSerializer,
                             RecipeSerializer, SetPasswordSerializer,
                             SubscriptionSerializer, TagSerializer,
                             UserCreateSerializer, UserSerializer)
from django.db.models import Sum
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipe.models import (Ingredients, Recipe, RecipeIngredients,
                           ShoppingList, Subscription, Tags, User)
from rest_framework import exceptions, filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('email', 'username')
    pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny,)
    serializer_class = UserCreateSerializer

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return UserSerializer
        return UserCreateSerializer

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserSerializer(request.user)
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
        serializer = SubscriptionSerializer(
            paginate_queryset,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                author, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=request.user,
                                        author=author)
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
    filterset_fields = ('author', 'tags')
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    serializer_class = RecipeSerializer

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipeingredients__ingredients', 'tags')
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
                    'Рецепт уже добавен в избранное.')
            FavoritesList.objects.create(user=user, recipe=recipe)
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
                    'Рецепт уже в списке покупок.')
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
        text = 'Список покупок:\n'
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
    search_fields = ('name', )
    ordering_fields = ('name', )
    permission_classes = (AllowAny,)
    serializer_class = IngredientsSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        ingredient_query = self.request.query_params.get('name')
        if ingredient_query:
            for i in range(1, len(ingredient_query) + 1):
                ingredient_name = ingredient_query[:i]
                queryset = queryset.filter(name__istartswith=ingredient_name)
        queryset = queryset.annotate(lower_name=Lower('name'))
        queryset = queryset.order_by('lower_name')
        return queryset


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None
