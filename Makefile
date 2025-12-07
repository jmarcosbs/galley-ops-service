.PHONY: watch bash stop build serve deploy

PORT ?= 8000
ENV_FILE ?= .env
PROD_COMPOSE_FILE ?= docker-compose-production.yml

watch:
	docker compose up -d
	docker compose logs --since 10m -f

bash:
	docker compose exec web bash

stop:
	docker compose down

build:
	docker compose build

serve:
	@echo "Starting Django server on port $(PORT)"
	DJANGO_SETTINGS_MODULE=core.settings python -m daphne -b 0.0.0.0 -p $(PORT) core.asgi:application

deploy:
	docker compose --env-file $(ENV_FILE) -f $(PROD_COMPOSE_FILE) up -d --build
