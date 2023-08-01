from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.validators import validate_time
from constants import COLOUR_LENGTH, SLUG_NAME_LENGTH
from users.models import User


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='no_self_subscribe'
            ),
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe'
            )

        ]

    def __str__(self):
        return f'{self.user} {self.author}'


class Tags(models.Model):
    name = models.CharField(
        'Название тега',
        max_length=SLUG_NAME_LENGTH,
        help_text='Название',
        unique=True
    )
    color = ColorField(
        'Цвет тега',
        format='hexa',
        max_length=COLOUR_LENGTH,
        help_text='Цвет',
        unique=True
    )
    slug = models.SlugField(
        'Идентификатор тега',
        max_length=SLUG_NAME_LENGTH,
        help_text='Идентификатор тега',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=SLUG_NAME_LENGTH,
        help_text='Название ингредиента'
    )
    measurement_units = models.CharField(
        'Единицы измерения',
        max_length=SLUG_NAME_LENGTH,
        help_text='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_units'],
                name='name_measurement_units'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор')
    name = models.CharField(
        'Название рецепта',
        max_length=SLUG_NAME_LENGTH,
        help_text='Название',
        unique=True
    )
    image = models.ImageField('Картинка',
                              upload_to='recipe/',
                              blank=True,
                              null=True,
                              default=None
                              )
    text = models.TextField('Описание',
                            blank=True,
                            null=True)
    ingredients = models.ManyToManyField(Ingredients,
                                         related_name='recipe_ingredients',
                                         through='RecipeIngredients',
                                         through_fields=(
                                             'recipe',
                                             'ingredients'),
                                         verbose_name='Ингредиенты')
    tags = models.ManyToManyField(Tags, verbose_name='Тег')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=[validate_time,
                    MaxValueValidator(240),
                    MinValueValidator(1)], blank=True, null=True,)
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='Рецепт'
    )
    ingredients = models.ForeignKey(Ingredients,
                                    on_delete=models.CASCADE,
                                    related_name='recipeingredients',
                                    verbose_name='Ингредиенты')
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MaxValueValidator(2000), MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        # ordering = ('recipe',)

    def __str__(self):
        return f'{self.recipe} {self.ingredients}'


class CommonDataAbstractModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True


class FavoritesList(CommonDataAbstractModel):

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.user}'


class ShoppingList(CommonDataAbstractModel):

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_shoppinglist'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.user}'
