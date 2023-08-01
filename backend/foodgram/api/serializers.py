from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from api.validators import validate_amount, validate_username
from recipe.models import (FavoritesList,
                           Ingredients,
                           Recipe,
                           RecipeIngredients,
                           ShoppingList,
                           Subscription,
                           Tag,
                           User,
                           EMAIL_LENGTH,
                           USERNAME_LENGTH)


class UserSerializer(UserSerializer):
    """Сериализатор юзера."""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_subscribed'
    )

    def get_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания юзера."""
    username = serializers.CharField(
        required=True,
        max_length=USERNAME_LENGTH,
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

    def update_password(self, instance, validated_data):
        if (validated_data['current_password']
           == validated_data['new_password']):
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от старого.'}
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор тега."""

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('id',)


class IngredientsSerializer(serializers.ModelSerializer):
    """ Сериализатор ингредиентов."""

    class Meta:
        model = Ingredients
        fields = '__all__'
        read_only_fields = ('id',)


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """ Сериализатор ингредиентов для рецепта."""
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_units = serializers.ReadOnlyField(
        source='ingredients.measurement_units'
        )

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
    cooking_time = serializers.IntegerField()
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = RecipeIngredientsSerializer(
        many=True,
        read_only=True,
        source='recipeingredients')
    is_favorited = serializers.SerializerMethodField(
        method_name='get_favorited'
        )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_shopping_cart'
        )

    def get_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return FavoritesList.objects.filter(user=user, recipe=obj).exists()

    def get_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingList.objects.filter(user=user, recipe=obj).exists()

    class Meta:
        model = Recipe
        fields = ('id', 'tag',
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
    tag = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = RecipeIngredientsCreateSerializer(
        many=True)

    def create_ingredients(self, ingredients, recipe):
        for ingredient_data in ingredients:
            amount = ingredient_data['amount']
            ingredient_id = ingredient_data.get('id')
            if ingredient_id:
                ingredient = get_object_or_404(Ingredients, pk=ingredient_id)
                RecipeIngredients.objects.create(
                    recipe=recipe,
                    ingredients=ingredient,
                    amount=amount)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tag = validated_data.pop('tag')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tag.set(tag)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tag' in validated_data:
            instance.tag.set(
                validated_data.pop('tag'))
        return super().update(
            instance, validated_data)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tag',
                  'image', 'name',
                  'text', 'cooking_time', 'author')
        read_only_fields = ('author',)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписок, список авторов."""
    recipes = serializers.SerializerMethodField(method_name='get_recipe')
    recipe_count = serializers.SerializerMethodField(
        method_name='get_recipe_count'
    )
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_subscribed'
    )

    def get_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()

    def get_recipe(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeSerializer(
            recipes,
            many=True).data

    def get_recipe_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipe_count')


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписок, подписка на автора."""
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_subscribed'
        )
    recipes = RecipeSerializer(many=True, read_only=True)
    recipe_count = serializers.SerializerMethodField(
        method_name='get_recipe_count'
        )

    def validate(self, obj):
        if (self.context['request'].user == obj):
            raise serializers.ValidationError({'errors': 'Ошибка подписки.'})
        return obj

    def get_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()

    def get_recipe_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipe_count')
