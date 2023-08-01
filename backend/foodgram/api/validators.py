import re

from django.core.exceptions import ValidationError
from rest_framework import serializers


def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError(f'Недопустипое имя - {value}!')
    if re.search(r'^[-a-zA-Z0-9_]+$', value) is None:
        raise ValidationError('Недопустимые символы')


def validate_time(cooking_time):
    if cooking_time <= 0:
        raise serializers.ValidationError(
            'Время приготовления должно быть больше 1 минуты')
    return cooking_time


def validate_amount(amount):
    if amount <= 0:
        raise serializers.ValidationError(
            'Минимаьное количество ингредиентов - 1')
    return amount
