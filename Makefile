#!make

SHELL := /bin/bash

runserver:
	@bash bin/run_server.sh dev

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

scalingo-prod-shell:
	@scalingo --app mec-connect-prod --region osc-secnum-fr1 run bash

scalingo-staging-shell:
	@scalingo --app mec-connect-staging --region osc-fr1 run bash
