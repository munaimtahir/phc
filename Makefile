run:
	python manage.py runserver 0.0.0.0:8000

check:
	python manage.py check

migrate:
	python manage.py migrate

test:
	pytest

lint:
	ruff check .

docker-up:
	docker compose up -d --build

docker-logs:
	docker compose logs -f --tail=100 web

docker-down:
	docker compose down
