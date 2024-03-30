COMPOSE_BASE := docker-compose
LOG_FILE := build.log

init-venv:
	python3 -m venv .venv

pytest:
	pytest -v fastapi;

init:
	$(COMPOSE_BASE) up airflow-init;
build-up:
	$(COMPOSE_BASE) up -d --build --remove-orphans;

up:	
	$(COMPOSE_BASE) up;

restart:	
	$(COMPOSE_BASE) restart;

down:
	$(COMPOSE_BASE) down;
	