from api.validators import validate_username
from constants import EMAIL_LENGTH, USERNAME_PASSWORD_LENGTH
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        'Логин',
        unique=True,
        blank=False,
        null=False,
        max_length=USERNAME_PASSWORD_LENGTH,
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
        max_length=USERNAME_PASSWORD_LENGTH
    )
    last_name = models.CharField(
        'Фамилия',
        blank=True,
        null=True,
        max_length=USERNAME_PASSWORD_LENGTH
    )
    password = models.CharField(max_length=USERNAME_PASSWORD_LENGTH)
    is_subscribed = models.ManyToManyField(
        to='self',
        through='recipe.Subscription',
        through_fields=('user', 'author'),
        related_name='is_following',
        symmetrical=False,
    )

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
