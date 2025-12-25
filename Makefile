.PHONY: watch bash stop build serve deploy logs

# Força bash (evita problemas com sh)
SHELL := /bin/bash

# Variáveis configuráveis
PORT ?= 8000
ENV_FILE ?= .env
COMPOSE ?= docker-compose
PROD_COMPOSE_FILE ?= docker-compose-production.yml

# -------- DEV --------

watch:
	$(COMPOSE) up -d
	$(COMPOSE) logs --since 10m -f

logs:
	$(COMPOSE) logs -f

bash:
	$(COMPOSE) exec web bash

stop:
	$(COMPOSE) down

build:
	$(COMPOSE) build

# -------- DJANGO LOCAL (sem docker) --------

serve:
	@echo "Starting Django (Daphne) on port $(PORT)"
	DJANGO_SETTINGS_MODULE=core.settings \
	python -m daphne -b 0.0.0.0 -p $(PORT) core.asgi:application

# -------- PRODUÇÃO --------

deploy:
	$(COMPOSE) --env-file $(ENV_FILE) \
		-f $(PROD_COMPOSE_FILE) \
		up -d --build
	$(COMPOSE) --env-file $(ENV_FILE) \
		-f $(PROD_COMPOSE_FILE) \
		exec web python manage.py migrate
	docker system prune -af --volumes

run:
	$(COMPOSE) --env-file $(ENV_FILE) \
		-f $(PROD_COMPOSE_FILE) \
		up -d
