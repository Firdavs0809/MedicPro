up:
	docker-compose up --build

down:
	docker-compose down -v

logs:
	docker-compose logs -f backend

migrate:
	docker-compose exec backend python manage.py migrate

createsuperuser:
	docker-compose exec backend python manage.py createsuperuser

shell:
	docker-compose exec backend python manage.py shell
