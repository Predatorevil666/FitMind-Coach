# FitMind Coach - Deployment Guide

## Production Deployment

### 1. Настройка GitLab CI/CD

#### Переменные окружения в GitLab:
Перейдите в **Settings** → **CI/CD** → **Variables** и добавьте:

```
SSH_PRIVATE_KEY: ваш_приватный_ssh_ключ_для_vps
SSH_KNOWN_HOSTS: результат команды ssh-keyscan -H 89.169.190.114
CI_REGISTRY_USER: root
CI_REGISTRY_PASSWORD: ваш_пароль_от_gitlab
POSTGRES_DB: fitmind_prod
POSTGRES_USER: fitmind_user
POSTGRES_PASSWORD: ваш_пароль_для_базы
SECRET_KEY: сгенерированный_секретный_ключ
ALGORITHM: HS256
ACCESS_TOKEN_EXPIRE_MINUTES: 30
BOT_TOKEN: токен_вашего_telegram_бота
MISTRAL_API_KEY: ваш_ключ_mistral_api
```

### 2. Настройка VPS

#### Подключение к VPS:
```bash
ssh -p 58934 batogov@89.169.190.114
```

#### Создание папки проекта:
```bash
mkdir -p /home/batogov/fitmindcoach
cd /home/batogov/fitmindcoach
```

#### Создание .env файла:
```bash
nano .env
```

Содержимое .env:
```bash
# Database Configuration
POSTGRES_DB=fitmind_prod
POSTGRES_USER=fitmind_user
POSTGRES_PASSWORD=your_secure_password_here

# API Configuration
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here
API_URL=http://api:8000

# AI Configuration
MISTRAL_API_KEY=your_mistral_api_key_here

# GitLab CI/CD Variables
CI_REGISTRY=fitmindlab.hopto.org:5050
CI_REGISTRY_IMAGE=fitmindlab.hopto.org:5050/root/fitmind-coach
CI_COMMIT_SHA=latest
CI_COMMIT_TAG=latest
```

#### Копирование docker-compose.prod.yml:
```bash
# Скопируйте файл с локальной машины
scp -P 58934 docker-compose.prod.yml batogov@89.169.190.114:/home/batogov/fitmindcoach/
```

### 3. Первый запуск

#### Запуск сервисов:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### Проверка статуса:
```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. Автоматический деплой

#### После настройки CI/CD:
1. Пустието изменения в ветку `dev`
2. Создайте Merge Request в GitLab
3. Мержите `dev` в `main`
4. GitLab автоматически:
   - Соберет Docker образы
   - Загрузит их в Container Registry
   - Развернет на VPS

### 5. Мониторинг

#### Проверка логов:
```bash
# API логи
docker-compose -f docker-compose.prod.yml logs -f api

# Bot логи
docker-compose -f docker-compose.prod.yml logs -f bot

# База данных
docker-compose -f docker-compose.prod.yml logs -f db
```

#### Проверка здоровья сервисов:
```bash
# API health check
curl http://localhost:8000/healthz

# Проверка статуса контейнеров
docker-compose -f docker-compose.prod.yml ps
```

### 6. Обновление

#### Ручное обновление:
```bash
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

#### Автоматическое обновление:
Просто пустието в `main` - GitLab сделает все автоматически!

### 7. Troubleshooting

#### Если миграции не применяются:
```bash
docker-compose -f docker-compose.prod.yml logs migrate
```

#### Если API не запускается:
```bash
docker-compose -f docker-compose.prod.yml logs api
```

#### Если бот не работает:
```bash
docker-compose -f docker-compose.prod.yml logs bot
```

### 8. Безопасность

- Все секреты хранятся в GitLab переменных
- SSH ключи для безопасного подключения
- База данных изолирована в Docker сети
- Nginx для проксирования запросов

### 9. Масштабирование

#### Добавление реплик:
```yaml
# В docker-compose.prod.yml
api:
  deploy:
    replicas: 3
```

#### Load balancer:
```yaml
nginx:
  ports:
    - "80:80"
    - "443:443"
  depends_on:
    - api
```

## Структура файлов

```
fitmindcoach/
├── .env                          # Переменные окружения
├── docker-compose.prod.yml       # Production конфигурация
├── nginx/                        # Nginx конфигурация
│   ├── nginx.conf
│   └── ssl/
└── logs/                         # Логи приложения
```
