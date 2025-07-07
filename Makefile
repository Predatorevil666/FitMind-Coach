.PHONY: run-api run-api-direct run-bot migrate alembic-init alembic-migrate alembic-upgrade lint create-superuser

run-api:
	uvicorn api.main:app --host 0.0.0.0 --port 8003 --reload

run-api-direct:
	python -m api.main

run-bot:
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
