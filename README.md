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
# Клонируем репозиторий
git clone https://github.com/whyourelated/foodgram-st.git
cd foodgram-st
```

### 2. Настраиваем переменные окружения
```bash
# Переходим в директорию с docker-compose
cd infra

# Создаем файл .env
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
# Собираем и запускаем контейнеры
docker-compose up -d

# Применяем миграции
docker-compose exec backend python manage.py migrate

# Создаем суперпользователя
docker-compose exec backend python manage.py createsuperuser

# Загружаем тестовые данные
docker-compose exec backend python manage.py loaddata
```

### 4. Проверяем работу проекта
- Откройте в браузере http://localhost
- Проверьте работу админ-панели: http://localhost/admin
- Проверьте API документацию: http://localhost/api/docs

## Тестовые данные
После загрузки тестовых данных будут созданы:
- Суперпользователь (admin/admin)
- Тестовые пользователи (test_user1/testpass123, test_user2/testpass123)
- Тестовые рецепты и ингредиенты

## Возможные проблемы и их решение

### 1. Не запускаются контейнеры
```bash
# Проверяем логи
docker-compose logs

# Проверяем статус контейнеров
docker-compose ps
```

### 2. Проблемы с базой данных
```bash
# Проверяем подключение к базе
docker-compose exec db psql -U postgres

# Сбрасываем базу и применяем миграции заново
docker-compose down -v
docker-compose up -d
docker-compose exec backend python manage.py migrate
```

## Полезные команды

### Работа с Docker
```bash
# Посмотреть запущенные контейнеры
docker ps

# Посмотреть логи
docker-compose logs -f

# Перезапустить контейнеры
docker-compose restart

# Остановить все контейнеры
docker-compose down
```

### Работа с Django
```bash
# Создать миграции
docker-compose exec backend python manage.py makemigrations

# Применить миграции
docker-compose exec backend python manage.py migrate

# Создать суперпользователя
docker-compose exec backend python manage.py createsuperuser

# Собрать статические файлы
docker-compose exec backend python manage.py collectstatic
```

## Автор
whyourelated - разработчик проекта Foodgram