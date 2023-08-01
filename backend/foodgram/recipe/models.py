from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from api.validators import validate_username, validate_time

USERNAME_LENGTH = 150
EMAIL_LENGTH = 254
SLUG_LENGTH = 50
ART_LENGTH = 256
COLOUR_LENGTH = 10
PASSWORD_LENGTH = 50


class User(AbstractUser):
    username = models.CharField(
        'Логин',
        unique=True,
        blank=False,
        null=False,
        max_length=USERNAME_LENGTH,
        validators=(validate_username,)
    )
    email = models.EmailField(
        'e-mail адрес',
        unique=True,
        blank=False,
        max_length=EMAIL_LENGTH
    )
    first_name = models.CharField(
        'Имя',
        blank=True,
        null=True,
        max_length=USERNAME_LENGTH
    )
    last_name = models.CharField(
        'Фамилия',
        blank=True,
        null=True,
        max_length=USERNAME_LENGTH
    )
    password = models.CharField(max_length=PASSWORD_LENGTH)

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username')
        ]

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} {self.author}'


class CommonDataAbstractModel(models.Model):

    class Meta:
        abstract = True

    name = models.CharField('Название', max_length=ART_LENGTH)
    slug = models.SlugField('Идентификатор',
                            max_length=SLUG_LENGTH,
                            unique=True)


class Tag(CommonDataAbstractModel):
    name = models.CharField(
        max_length=ART_LENGTH,
        help_text='Название',
        unique=True
    )
    colour = models.CharField(
        max_length=COLOUR_LENGTH,
        help_text='Цвет',
        unique=True,
        validators=[
            RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Цвет должен быть в формате HEX-кода.'
            )
        ]

    )
    slug = models.SlugField(
        max_length=SLUG_LENGTH,
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
        max_length=ART_LENGTH,
        help_text='Название ингредиента'
    )
    measurement_units = models.CharField(
        max_length=ART_LENGTH,
        help_text='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор')
    name = models.CharField(
        max_length=ART_LENGTH,
        help_text='Название'
    )
    image = models.ImageField('Картинка',
                              upload_to='recipe/',
                              null=True,
                              default=None
                              )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(Ingredients,
                                         through='RecipeIngredients',
                                         through_fields=(
                                             'recipe',
                                             'ingredients'),
                                         verbose_name='Ингредиенты')
    tag = models.ManyToManyField(Tag,
                                 verbose_name='Тег'
                                 )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=[validate_time,
                    MinValueValidator(1)]
    )
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


class FavoritesList(CommonDataAbstractModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favoriteslist',
        verbose_name='Пользователь'
    )
    recipe = models.ManyToManyField(
        Recipe,
        related_name='favoriteslist',
        verbose_name='Рецепт в избранном'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.recipe} {self.user}'


class ShoppingList(CommonDataAbstractModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppinglist_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppinglist_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_shoppinglist'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.user}'


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
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f'{self.recipe} {self.ingredients}'
