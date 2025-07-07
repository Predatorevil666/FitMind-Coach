# FitMind-Coach

## Установка и настройка

Если вы склонировали этот проект, выполните следующие шаги:

1. **Установите Poetry**, если он еще не установлен:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. ## Установка плагина shell для Poetry

На новой машине, чтобы использовать команду `poetry shell`, необходимо установить плагин `poetry-plugin-shell`. Для этого выполните следующую команду:

```bash
poetry self add poetry-plugin-shell
```

После установки плагина вы сможете активировать виртуальное окружение с помощью команды:

```bash
poetry shell
```

3. **Клонируйте репозиторий**:
   ```bash
   git clone <URL_вашего_репозитория>
   cd <имя_папки_проекта>
   ```

4. **Установите зависимости**:
   ```bash
   poetry install
   ```

5. **Активируйте виртуальное окружение**:
   ```bash
   poetry shell
   ```

6. **Запускайте команды**:
   Если вы не хотите активировать виртуальное окружение, используйте:
   ```bash
   poetry run <команда>
   ```

## Настройка pre-commit хуков

Для настройки pre-commit хуков выполните:

```bash
poetry run pre-commit install
```

После этого при каждом коммите будут автоматически запускаться проверки кода с помощью ruff и mypy.

## Настройка переменных окружения

1. **Создайте файл .env** в корне проекта на основе .env.example:
   ```bash
   cp .env.example .env
   ```

2. **Отредактируйте файл .env**, установив нужные значения для переменных окружения:
   ```
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

   # JWT
   SECRET_KEY=your_secret_key

   # Общие настройки
   TZ=Europe/Moscow
   DEBUG=False
   ```

## Создание суперпользователя

После настройки базы данных и выполнения миграций вы можете создать суперпользователя с правами администратора:

```bash
make create-superuser
```

или

```bash
poetry run python -m api.create_superuser
```

Вам будет предложено ввести email, имя пользователя и пароль для нового суперпользователя.

## Запуск бота
(ник бота - @fitmindcoach2025_bot)

### Запуск в режиме разработки

1. **Запустите бота**:
   ```bash
   poetry run python -m bot.main
   ```

2. **Запустите API**:
   ```bash
   poetry run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

Или используйте команды из Makefile:
```bash
make run-bot  # Для запуска бота
make run-api  # Для запуска API
```

### Запуск с помощью Docker

1. **Запуск с помощью Docker Compose**:
   ```bash
   docker-compose up -d  # Запуск в фоновом режиме
   ```


## Логирование

Бот настроен для логирования сообщений в консоль и в файл. Логи сохраняются в директории `logs/bot.log`. Настройки логирования находятся в файле `bot/logger.py`.

Логи включают:
- Информацию о запуске и остановке бота
- Ошибки при выполнении операций
- Другие важные события

Файлы логов автоматически ротируются при достижении размера 10MB, хранятся до 5 файлов истории.
