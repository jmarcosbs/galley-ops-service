.PHONY: watch bash stop build

watch:
	docker compose up -d
	docker compose logs --since 10m -f

bash:
	docker compose exec web bash

stop:
	docker compose down

build:
	docker compose build
