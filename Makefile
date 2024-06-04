#!make

SHELL := /bin/bash

runserver:
	@python manage.py runserver 0.0.0.0:8002

runworker:
	@celery -A mec_connect.worker worker -l info --concurrency=1

precommit:
	@pre-commit run --all-files

test:
	@pytest -n auto --maxfail=3

migrate:
	@python manage.py migrate

admin:
	@xdg-open http://localhost:8002/admin