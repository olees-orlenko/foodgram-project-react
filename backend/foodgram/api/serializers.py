import re

from api.validators import validate_amount, validate_username
from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipe.models import (FavoritesList, Ingredients, Recipe,
                           RecipeIngredients, ShoppingList, Subscription, Tags)
from rest_framework import serializers
from users.models import EMAIL_LENGTH, USERNAME_PASSWORD_LENGTH, User


class UserSerializer(UserSerializer):
    """Сериализатор юзера."""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_subscribed'
    )

    def get_subscribed(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return Subscription.objects.filter(user=request.user,
                                               author=obj).exists()
        return False

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания юзера."""
    username = serializers.CharField(
        required=True,
        max_length=USERNAME_PASSWORD_LENGTH,
        validators=[
            validate_username]
    )
    email = serializers.EmailField(required=True, max_length=EMAIL_LENGTH)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password'
        )

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                f'Имя{value} уже занято')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(f'email{value} уже занят')
        return value


class SetPasswordSerializer(serializers.ModelSerializer):
    """Сериализатор изменения пароля."""
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'new_password',
            'current_password'
        )

    def update_password(self, instance, validate_data):
        if validate_data['current_password'] == validate_data['new_password']:
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от старого.'}
            )
        instance.set_password(validate_data['new_password'])
        instance.save()
        return validate_data


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор тега."""

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id',)


class IngredientsSerializer(serializers.ModelSerializer):
    """ Сериализатор ингредиентов."""

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_units')
        read_only_fields = ('id',)


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """ Сериализатор ингредиентов для рецепта."""
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_units = serializers.ReadOnlyField(
        source='ingredients.measurement_units')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_units', 'amount')


class RecipeIngredientsCreateSerializer(serializers.ModelSerializer):
    """ Сериализатор создания ингредиентов для рецепта."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=[validate_amount,
                    MinValueValidator(1)], write_only=True)

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    """Список рецептов без ингридиентов."""
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор получения рецепта."""
    name = serializers.ReadOnlyField()
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    cooking_time = serializers.IntegerField()
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = RecipeIngredientsSerializer(
        many=True,
        read_only=True,
        source='recipeingredients')
    is_favorited = serializers.SerializerMethodField(
        method_name='get_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_shopping_cart')

    def get_favorited(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return FavoritesList.objects.filter(user=request.user,
                                                recipe=obj).exists()
        return False

    def get_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return ShoppingList.objects.filter(user=request.user,
                                               recipe=obj).exists()
        return False

    class Meta:
        model = Recipe
        fields = ('id', 'tags',
                  'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image',
                  'text', 'cooking_time')
        read_only_fields = ('id',
                            'author',
                            'name',
                            'is_favorited',
                            'is_in_shopping_cart')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """ Сериализатор создания рецепта."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True
    )
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = RecipeIngredientsCreateSerializer(
        many=True)
    cooking_time = serializers.IntegerField()

    def validate_name(self, value):
        if re.match(r'^[0-9\W]+$', value):
            raise serializers.ValidationError(
                'Название рецепта не может состоять только из цифр и знаков.'
            )
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Добавьте тег.'
            )
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Добавьте ингредиент.'
            )
        ingredients = [item['id'] for item in value]
        for ingredient in ingredients:
            if ingredients.count(ingredient) > 1:
                raise serializers.ValidationError(
                    'Такой ингредиент уже есть.'
                )
        return value

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 1')
        return cooking_time

    def create_ingredients(self, ingredients, recipe):
        for ingredient_data in ingredients:
            amount = ingredient_data['amount']
            ingredient_id = ingredient_data['id']
            if ingredient_id:
                ingredient = get_object_or_404(Ingredients, pk=ingredient_id)
                RecipeIngredients.objects.create(
                    recipe=recipe,
                    ingredients=ingredient,
                    amount=amount)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self.create_ingredients(ingredients, instance)
        instance.tags.set(validated_data.pop('tags'))
        return super().update(
            instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags',
                  'image', 'name',
                  'text', 'cooking_time', 'author')
        read_only_fields = ('author',)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписок, список авторов."""
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    recipes = serializers.SerializerMethodField(method_name='get_recipe')
    recipe_count = serializers.SerializerMethodField(
        method_name='get_recipe_count'
    )
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_subscribed'
    )

    def validate(self, obj):
        author = self.instance
        user = self.context.get('request').user
        if user == author:
            raise serializers.ValidationError({
                'detail': 'Вы не можете подписаться на самого себя!'
            })
        if Subscription.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError({
                'detail': 'Вы уже подписаны на этого пользователя!'
            })
        return obj

    def get_subscribed(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return Subscription.objects.filter(user=request.user,
                                               author=obj).exists()
        return False

    def get_recipe(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return SubscribeSerializer(
            recipes,
            many=True).data

    def get_recipe_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipe_count')
        exclude_fields = ('tags',
                          'text',
                          'is_favorited',
                          'is_in_shopping_cart')


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписок, подписка на автора."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
