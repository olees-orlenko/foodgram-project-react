## Описание проекта
«Продуктовый помощник», на котором пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», скачивать список продуктов, необходимых для приготовления выбранных блюд.
Ссылка на сайт: https://foodgram.serveblog.net
логин: admin
пароль: admin

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

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```