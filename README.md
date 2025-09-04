# 🏋️ FitMind-Coach

**FitMind-Coach** — это современное приложение для фитнес-коучинга и планирования тренировок, которое объединяет в себе Telegram бота с ИИ-помощником и мощное REST API для управления тренировками, питанием и лабораторными показателями.

## Автор проект
* [Alexander Batogov](https://github.com/Predatorevil666)

## 📋 Описание проекта

FitMind-Coach помогает пользователям:
- 🎯 Ставить и достигать фитнес-цели
- 📊 Отслеживать прогресс тренировок и питания
- 🧠 Получать персонализированные советы от ИИ (Mistral AI)
- 📱 Удобно взаимодействовать через Telegram бота
- 🔬 Анализировать лабораторные показатели здоровья

**Telegram бот:** [@fitmindcoach2025_bot](https://t.me/fitmindcoach2025_bot)

## 🚀 Технологический стек

### 🐍 **Backend (API)**
- **Python 3.12+** — основной язык программирования
- **FastAPI** — современный веб-фреймворк для создания REST API
- **Uvicorn** — ASGI сервер для высокопроизводительного запуска
- **Pydantic** — валидация данных и создание схем API
- **Python-Jose** — работа с JWT токенами для безопасной аутентификации
- **Passlib + bcrypt** — надежное хеширование паролей

### 🤖 **Telegram Bot**
- **Aiogram 3.20** — современная асинхронная библиотека для Telegram ботов
- **Aiohttp** — асинхронные HTTP запросы к API

### 🗄️ **База данных**
- **PostgreSQL** — основная реляционная база данных
- **SQLAlchemy 2.0 + asyncio** — современная асинхронная ORM
- **Asyncpg** — высокопроизводительный драйвер для PostgreSQL
- **Alembic** — система миграций базы данных
- **Aiosqlite** — поддержка SQLite для разработки

### 🧠 **ИИ и шаблоны**
- **Mistral AI** — интеграция с языковой моделью для фитнес-советов
- **Jinja2** — шаблонизатор для промптов ИИ

### 🐳 **DevOps и деплой**
- **Docker + Docker Compose** — контейнеризация и оркестрация
- **Nginx** — веб-сервер и обратный прокси
- **Poetry** — управление зависимостями и виртуальным окружением

### 🛠️ **Инструменты разработки**
- **Ruff** — современный линтер и форматтер кода
- **MyPy** — статическая типизация
- **Pre-commit** — Git хуки для контроля качества кода

## 🏗️ Архитектура

Проект построен по **микросервисной архитектуре**:

- **API сервис** — обрабатывает HTTP запросы и бизнес-логику
- **Bot сервис** — Telegram бот, взаимодействующий с API
- **Database сервис** — PostgreSQL база данных
- **Migration сервис** — автоматическое применение миграций при запуске

## 🛠️ Установка и настройка

### 1. **Установка Poetry**
```bash
curl -sSL https://install.python-poetry.org | python3 -
poetry self add poetry-plugin-shell  # Для поддержки poetry shell
```

### 2. **Клонирование и установка зависимостей**
```bash
git clone <URL_вашего_репозитория>
cd FitMind-Coach
poetry install
poetry shell  # Активация виртуального окружения
```

### 3. **Настройка pre-commit хуков**
```bash
poetry run pre-commit install
```

### 4. **Настройка переменных окружения**
Создайте файл `.env` в корне проекта:

```bash
# База данных
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/fitmind
POSTGRES_PASSWORD=postgres
POSTGRES_USER=postgres
POSTGRES_DB=fitmind

# API
API_HOST=0.0.0.0
API_PORT=8000
API_URL=http://api:8003/api/v1

# Бот
TG_TOKEN=your_telegram_bot_token
BOT_ADMIN_ID=your_telegram_id

# ИИ
MISTRAL_API_KEY=your_mistral_api_key

# JWT
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Общие настройки
TZ=Europe/Moscow
DEBUG=False
```

## 🚀 Запуск приложения

### Запуск с Docker (рекомендуется)
```bash
docker-compose up -d
```

### Запуск в режиме разработки
```bash
# API сервер
make run-api
# или
poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Telegram бот
make run-bot
# или
poetry run python -m bot.main
```

### Создание суперпользователя
```bash
make create-superuser
# или
poetry run python -m api.create_superuser
```

## 📊 Мониторинг и логи

### Логирование
Приложение настроено для детального логирования:
- **Расположение:** `logs/` директория
- **Ротация:** автоматическая при достижении 10MB
- **История:** хранится до 5 файлов

### Health checks
- **API:** `GET /healthz` — проверка работоспособности API
- **Database:** автоматические проверки подключения

## 🔧 Полезные команды

```bash
# Запуск API
make run-api

# Запуск бота
make run-bot

# Создание суперпользователя
make create-superuser

# Применение миграций
make migrate

# Проверка кода
poetry run ruff check .
poetry run mypy .

# Форматирование кода
poetry run ruff format .
```

## 📱 Основные возможности бота

- **🔐 Авторизация:** регистрация, логин, автоматическая привязка Telegram
- **👤 Профили:** создание и управление фитнес-профилями
- **🏋️ Тренировки:** планирование и отслеживание тренировок
- **🍽️ Питание:** учет приемов пищи и калорий
- **🔬 Анализы:** отслеживание лабораторных показателей
- **🧠 ИИ-советы:** персонализированные рекомендации

## 🤝 Разработка

### Структура проекта
```
FitMind-Coach/
├── api/           # FastAPI бэкенд
├── bot/           # Telegram бот
├── alembic/       # Миграции БД
├── nginx/         # Конфигурация Nginx
└── logs/          # Логи приложения
```

### Контрибуция
1. Fork репозитория
2. Создайте feature ветку
3. Убедитесь что код проходит линтеры
4. Создайте Pull Request

## 📄 Лицензия

Проект разработан Alexander Batogov (predatorevil666@mail.ru)

---

**FitMind-Coach** — ваш персональный ИИ-тренер в Telegram! 🚀
