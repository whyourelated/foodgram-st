# Foodgram - сервис для публикации рецептов 🍳

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

## Как запустить проект на сервере

### 1. Подготовка сервера
```bash
# Подключаемся к серверу
ssh username@your_server_ip

# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Docker и Docker Compose
sudo apt install docker.io docker-compose -y

# Добавляем текущего пользователя в группу docker
sudo usermod -aG docker $USER

# Перезаходим в систему для применения изменений
exit
ssh username@your_server_ip
```

### 2. Клонируем репозиторий
```bash
# Создаем директорию для проекта
mkdir foodgram
cd foodgram

# Клонируем репозиторий
git clone https://github.com/your-username/foodgram-st.git .
```

### 3. Настраиваем переменные окружения
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
POSTGRES_PASSWORD=your_secure_password
DB_HOST=db
DB_PORT=5432

SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=your_domain_or_ip
```

### 4. Настраиваем домен (если есть)
```bash
# Устанавливаем certbot для получения SSL-сертификата
sudo apt install certbot python3-certbot-nginx -y

# Получаем SSL-сертификат
sudo certbot --nginx -d your_domain.com
```

### 5. Запускаем проект
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

### 6. Проверяем работу проекта
- Откройте в браузере http://your_domain_or_ip
- Проверьте работу админ-панели: http://your_domain_or_ip/admin
- Проверьте API документацию: http://your_domain_or_ip/api/docs

## Как обновить проект
```bash
# Подключаемся к серверу
ssh username@your_server_ip

# Переходим в директорию проекта
cd foodgram

# Получаем изменения из репозитория
git pull

# Пересобираем и перезапускаем контейнеры
cd infra
docker-compose down
docker-compose up -d --build
```

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

### 3. Проблемы с правами доступа
```bash
# Проверяем права на директории
ls -la

# Исправляем права
sudo chown -R $USER:$USER .
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

## Безопасность
- Регулярно обновляйте систему и пакеты
- Используйте сложные пароли
- Настройте файрвол
- Используйте SSL-сертификат
- Регулярно делайте резервные копии базы данных

## Резервное копирование
```bash
# Создаем бэкап базы данных
docker-compose exec db pg_dump -U postgres > backup.sql

# Восстанавливаем из бэкапа
cat backup.sql | docker-compose exec -T db psql -U postgres
```

## Автор
[Ваше имя] - разработчик проекта Foodgram

## Лицензия
MIT License

