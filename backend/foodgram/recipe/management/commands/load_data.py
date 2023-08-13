import csv

from django.core.management import BaseCommand
from foodgram import settings
from recipe.models import Ingredients


class Command(BaseCommand):
    help = 'Загрузка ингредиентов в базу данных.'

    def handle(self, *args, **kwargs):
        data_path = settings.BASE_DIR
        with open(f'{data_path}/data/ingredients.csv',
                  'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file, delimiter=',')
            for row in csv_reader:
                _, created = Ingredients.objects.get_or_create(
                    name=row[0],
                    defaults={'measurement_units': row[1]}
                )
                if created:
                    self.stdout.write(f'Создан ингредиент: {row[0]}')
                else:
                    self.stdout.write(f'Ингредиент {row[0]} уже существует')
            self.stdout.write(self.style.SUCCESS('Данные успешно загружены.'))
