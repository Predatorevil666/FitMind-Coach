.PHONY: run-api run-api-direct run-bot run-bot-safe stop-bot status-bot migrate alembic-init alembic-migrate alembic-upgrade lint create-superuser up down logs restart deploy migrate-docker

run-api:
	uvicorn api.main:app --host 0.0.0.0 --port 8003 --reload

run-api-direct:
	python -m api.main

run-bot:
	python -m bot.main

run-all:
	uvicorn api.main:app --host 0.0.0.0 --port 8003 --reload &
	python -m bot.main

migrate:
	alembic upgrade head

alembic-init:
	alembic init alembic

alembic-migrate:
	alembic revision --autogenerate -m "$(message)"

alembic-upgrade:
	alembic upgrade head

create-superuser:
	python -m api.create_superuser

lint:
	pre-commit run --all-files

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

restart:
	docker compose restart

deploy: down up migrate-docker
	@echo "🚀 Развертывание завершено! API: http://localhost:8003"

migrate-docker:
	@echo "🔄 Применение миграций..."
	docker compose exec -T api bash -c 'export DATABASE_URL="postgresql://postgres:$${POSTGRES_PASSWORD}@db:5432/$${POSTGRES_DB}" && alembic upgrade head'
	@echo "✅ Миграции применены!"

create-superuser-docker:
	@echo "👤 Создание суперпользователя..."
	docker compose exec -T api python -m api.create_superuser

status-docker:
	@echo "📊 Статус сервисов:"
	docker compose ps
	@echo "📊 Статус миграций:"
	docker compose exec -T api bash -c 'export DATABASE_URL="postgresql://postgres:$${POSTGRES_PASSWORD}@db:5432/$${POSTGRES_DB}" && alembic current'

# GitLab deployment targets
gitlab-init:
	@echo "🔧 Инициализация GitLab репозитория..."
	git remote add gitlab http://130.193.42.202:2222/batogov/fitmind-coach.git || echo "Remote уже существует"
	git remote set-url gitlab http://130.193.42.202:2222/batogov/fitmind-coach.git

gitlab-push:
	@echo "📤 Отправка кода в GitLab..."
	git add .
	git commit -m "Update: $(shell date +%Y-%m-%d_%H:%M:%S)" || echo "Нет изменений для коммита"
	git push gitlab main

gitlab-deploy:
	@echo "🚀 Развертывание на VPS через GitLab..."
	ssh -p 58934 batogov@130.193.42.202 "cd /home/batogov/fitmind-coach && ./scripts/deploy.sh"

# Полный цикл: push + deploy
gitlab-full: gitlab-push gitlab-deploy

# Проверка статуса на VPS
vps-status:
	@echo "📊 Статус сервисов на VPS..."
	ssh -p 58934 batogov@130.193.42.202 "cd /home/batogov/fitmind-coach && docker compose ps"

# Логи с VPS
vps-logs:
	@echo "📋 Логи с VPS..."
	ssh -p 58934 batogov@130.193.42.202 "cd /home/batogov/fitmind-coach && docker compose logs --tail=50"
