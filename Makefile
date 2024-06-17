#!make

SHELL := /bin/bash

runserver:
	@python manage.py runserver 0.0.0.0:8002
	# @bash bin/run_server.sh

runworker:
	@bash bin/run_worker.sh

precommit:
	@pre-commit run --all-files

test:
	@pytest -n auto --maxfail=3

migrate:
	@python manage.py migrate

admin:
	@xdg-open http://localhost:8002/admin

freeze-reqs:
	@poetry lock --no-update
	@poetry export --without-hashes --without-urls | awk '{ print $$1 }' FS=';' > requirements.txt