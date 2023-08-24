# "Продуктовый помощник" Foodgram 
## Описание проекта
«Продуктовый помощник», на котором пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», скачивать список продуктов, необходимых для приготовления выбранных блюд.
Ссылка на сайт: https://foodgram.serveblog.net

## Технологии
•	Python 3.9
•	Django==3.2.3
•	djangorestframework==3.12.4
•	nginx
•	gunicorn==20.1.0

## Автор
[@olees-orlenko](https://github.com/olees-orlenko)

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/olees-orlenko/foodgram-project-react.git
```

```
cd foodgram-project-react
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Перейти в каталог infra
```
cd foodgram-project-react/infra
```

Создать файл .evn для хранения ключей:

```
SECRET_KEY='указать секретный ключ'
ALLOWED_HOSTS='указать имя или IP хоста'
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
DEBUG=False
```

Запустить docker-compose.production:

```
docker compose -f docker-compose.production.yml up
```

Выполнить миграции, сбор статики и загрузку ингредиентов:

```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input
docker compose -f docker-compose.production.yml exec backend python manage.py load_data
```

Создать суперпользователя, ввести почту, логин, пароль:

```
docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

