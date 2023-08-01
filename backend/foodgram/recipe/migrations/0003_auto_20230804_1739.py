# Generated by Django 3.2.3 on 2023-08-04 14:39

import api.validators
import colorfield.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0002_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='subscription',
            name='recipe_subscription_unique_relationships',
        ),
        migrations.AlterField(
            model_name='favoriteslist',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favoriteslist', to='recipe.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[api.validators.validate_time, django.core.validators.MaxValueValidator(240), django.core.validators.MinValueValidator(1)], verbose_name='Время приготовления в минутах'),
        ),
        migrations.AlterField(
            model_name='shoppinglist',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shoppinglist', to='recipe.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(default='#FFFFFFFF', help_text='Цвет', image_field=None, max_length=9, samples=None, unique=True, verbose_name='Цвет тега'),
        ),
        migrations.AddConstraint(
            model_name='favoriteslist',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_favorite'),
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.CheckConstraint(check=models.Q(('user', django.db.models.expressions.F('author')), _negated=True), name='no_self_subscribe'),
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_subscription'),
        ),
    ]