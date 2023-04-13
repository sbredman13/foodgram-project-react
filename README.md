https://github.com/sbredman13/foodgram-project-react/actions/workflows/foodgram_workflow/badge.svg


# "Продуктовый помощник" (Foodgram)

Проект достпуен по адресу: http://foodgramsbredman.myftp.org и 130.193.49.231

### Описание

Проект "Продуктовый помошник" (Foodgram) предоставляет пользователям следующие возможности:
  - регистрироваться
  - создавать свои рецепты и управлять ими (корректировать\удалять)
  - просматривать рецепты других пользователей
  - добавлять рецепты других пользователей в "Избранное" и в "Корзину"
  - подписываться на других пользователей и просматривать их рецепты
  - скачать список ингредиентов для рецептов, добавленных в "Корзину"

### Технологии
Python 3.7
Django 3.2.18 
Django Rest
React
Docker
PostgreSQL
nginx
gunicorn
Djoser


## База данных и переменные окружения

Проект использует базу данных PostgreSQL 
Для подключения и выполненя запросов к базе данных необходимо создать и заполнить файл ".env" с переменными окружения в папке "./infra/".

Шаблон для заполнения файла ".env":
```python
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS='Здесь указать имя или IP хоста' (Для локального запуска - 127.0.0.1)
```

---
## Команды для запуска

Перед запуском необходимо склонировать проект:
```bash
HTTPS: git clone https://github.com/sbredman13/foodgram-project-react.git
SSH: git clone git@github.com:sbredman13/foodgram-project-react.git
```

Cоздать и активировать виртуальное окружение:
```bash
python -m venv venv
```
```bash
Linux: source venv/bin/activate
Windows: source venv/Scripts/activate
```

И установить зависимости из файла requirements.txt:
```bash
python3 -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

Далее необходимо собрать образы для фронтенда и бэкенда.  
Из папки "./backend/foodgram/" выполнить команду:
```bash
docker build -t sbredman13/foodgram .
```

Из папки "./frontend/" выполнить команду:
```bash
docker build -t sbredman13/foodgram_frontend .
```

После создания образов можно создавать и запускать контейнеры.  
Из папки "./infra/" выполнить команду:
```bash
docker-compose up -d
```

После успешного запуска контейнеров выполнить миграции:
```bash
docker-compose exec backend python manage.py migrate
```

Создать суперюзера (Администратора):
```bash
docker-compose exec backend python manage.py createsuperuser
```

Собрать статику:
```bash
docker-compose exec backend python manage.py collectstatic --no-input
```

Теперь доступность проекта можно проверить по адресу [http://localhost/](http://localhost/)

---
## Заполнение базы данных 

С проектом поставляются данные об ингредиентах.  
Заполнить базу данных ингредиентами можно выполнив следующую команду из папки "./infra/":
```bash
docker-compose exec backend python manage.py Import_ingredients
```

Также необходимо заполнить базу данных тегами (или другими данными).  
Для этого требуется войти в [админ-зону](http://localhost/admin/)
проекта под логином и паролем администратора (пользователя, созданного командой createsuperuser).

---
## Техническая информация

Веб-сервер: nginx (контейнер nginx)  
Frontend фреймворк: React (контейнер frontend)  
Backend фреймворк: Django (контейнер backend)  
API фреймворк: Django REST (контейнер backend)  
База данных: PostgreSQL (контейнер db)

Веб-сервер nginx перенаправляет запросы клиентов к контейнерам frontend и backend, либо к хранилищам (volume) статики и файлов.  
Контейнер nginx взаимодействует с контейнером backend через gunicorn.  
Контейнер frontend взаимодействует с контейнером backend посредством API-запросов.

---
## Об авторе

Шапшинов Сергей Юрьевич  
Python-разработчик (Backend)  
Россия, г. Санкт-Петербург  
E-mail: sbredman13@icloud.com  
Telegram: @sbredman13

## Тестовые данные для входа в админку на боевом сервере

Логин: admin
Пароль: admin
