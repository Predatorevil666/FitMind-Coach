# Stage 1: Базовый образ для установки зависимостей
FROM python:3.12-slim as builder

# Установка Poetry
RUN pip install --no-cache-dir poetry

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock* ./

# Настройка Poetry для установки пакетов в систему, а не в виртуальное окружение
RUN poetry config virtualenvs.create false

# Установка зависимостей без dev-зависимостей и без установки текущего проекта
RUN poetry install --only main --no-interaction --no-ansi --no-root

# Stage 2: Финальный образ
FROM python:3.12-slim

# Установка curl для healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование установленных пакетов из builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копирование всего проекта для доступа к модулю api
COPY . /app/

# Установка переменной окружения для Python
ENV PYTHONPATH="/app:$PYTHONPATH"

# Создание директории для логов
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Экспонирование порта
EXPOSE 8003

# Запуск API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8003"]
