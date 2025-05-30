# Foodgram - сервис для публикации рецептов

## О проекте

Foodgram - это сервис для публикации рецептов. Здесь вы можете:
- Публиковать свои рецепты
- Подписываться на других авторов
- Добавлять понравившиеся рецепты в избранное
- Скачивать список покупок для выбранных рецептов

## Технологии
- Python 3.9
- Django 3.2
- Django REST Framework
- PostgreSQL
- Docker
- Nginx
- React

## Как запустить проект локально

### 1. Клонируем репозиторий
```bash
git clone https://github.com/whyourelated/foodgram-st.git
cd foodgram-st
```

### 2. Настраиваем переменные окружения
```bash
cd infra
nano .env
```

Добавляем в файл .env следующие переменные:
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Запускаем проект
```bash
docker-compose up -d --build
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py import_ingredients
docker-compose exec backend python manage.py collectstatic --no-input
```

### 4. Проверяем работу проекта
- [Главная страница](http://localhost)
- [Админ-панель](http://localhost/admin)
- [API документация](http://localhost/api/docs)

## Тестовые данные
После загрузки тестовых данных будут созданы:
- суперпользователь (создается командой createsuperuser)
- предзагруженные ингредиенты (загружаются командой import_ingredients)

## Автор
[whyourelated](https://github.com/whyourelated) - разработчик проекта Foodgram