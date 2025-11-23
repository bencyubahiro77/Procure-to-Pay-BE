# Makefile for a Django project (development -> production)
# Adapt variables below to your environment.

PROJECT_NAME := procure_to_pay
DJANGO_MANAGE := python manage.py

# Python / virtualenv
PYTHON := python3
VENV_DIR := my_venv
PIP := $(VENV_DIR)/bin/pip
PY := $(VENV_DIR)/bin/python

# Docker / registry
DOCKER := docker
DOCKER_COMPOSE := docker-compose
DOCKER_IMAGE := $(PROJECT_NAME):latest
DOCKER_REGISTRY ?= myregistry.example.com/$(PROJECT_NAME)
DOCKER_TAG ?= $(DOCKER_REGISTRY):$(shell date +%Y%m%d%H%M)
COMPOSE_FILE_DEV := docker-compose.yml
COMPOSE_FILE_PROD := docker-compose.prod.yml

# Django settings
DJANGO_SETTINGS_MODULE ?= procure_to_pay.settings
export DJANGO_SETTINGS_MODULE

# Files & directories
REQUIREMENTS := requirements.txt
STATIC_ROOT := staticfiles
MEDIA_ROOT := media

# Default target
.PHONY: help
help:
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Common targets:"
	@echo "  init                Create venv and install dependencies"
	@echo "  install             Install python deps (pip install -r requirements.txt)"
	@echo "  freeze              Freeze current venv to requirements.txt"
	@echo "  run                 Run local devserver (uses venv)"
	@echo "  migrate             Run migrations"
	@echo "  makemigrations      Make new migrations"
	@echo "  createsuperuser     Create django superuser"
	@echo "  collectstatic       Collect static files"
	@echo "  test                Run tests (pytest if available, else manage.py test)"
	@echo "  lint                Run formatters and linters (black, isort, flake8)"
	@echo "  docker-build        Build docker image"
	@echo "  docker-push         Push docker image to DOCKER_REGISTRY"
	@echo "  compose-up-dev      Start dev stack with docker-compose"
	@echo "  compose-up-prod     Start production stack with docker-compose -f docker-compose.prod.yml"
	@echo "  backup-db           Dump the database to backups/db-<date>.sql"
	@echo "  restore-db          Restore database from file (ARG=file path)"
	@echo "  disactivate         Disactivate venv and clean up temporary files"
	@echo "  activate		   Activate venv (prints command to source)"
	@echo "  clean               Clean up pyc, __pycache__, venv, staticfiles, build artifacts"
	@echo "  rebuild             Clean, init, install, migrate, collectstatic"
	@echo "  seed                Seed default users with roles"
	@echo ""
	@echo "Examples:"
	@echo "  make init"
	@echo "  make run"
	@echo "  make docker-build DOCKER_TAG=registry/$(PROJECT_NAME):v1.2.3"
	@echo ""

# ---------------------------
# Virtualenv and dependencies
# ---------------------------
.PHONY: init
init: $(VENV_DIR)/bin/activate install
	@echo "Virtualenv and packages installed."

$(VENV_DIR)/bin/activate:
	$(PYTHON) -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip setuptools wheel
	@touch $(VENV_DIR)/bin/activate

.PHONY: activate
activate:
	@echo "Run the following command to activate the virtual environment:"
	@echo "source $(VENV_DIR)/bin/activate"

.PHONY: install
install: $(VENV_DIR)/bin/activate
	@if [ -f "$(REQUIREMENTS)" ]; then \
	  $(PIP) install -r $(REQUIREMENTS); \
	else \
	  echo "No requirements.txt found — create one or run 'make freeze' from a venv"; \
	fi

.PHONY: freeze
freeze: $(VENV_DIR)/bin/activate
	$(PIP) freeze > $(REQUIREMENTS)
	@echo "Wrote $(REQUIREMENTS)"

.PHONY: disactivate
disactivate:
	rm -rf $(VENV_DIR)
	@echo "Virtual environment removed."

.PHONY: seed
seed: $(VENV_DIR)/bin/activate
	$(PY) $(DJANGO_MANAGE) seed_users

# ---------------------------
# Local dev helpers
# ---------------------------
.PHONY: run
run: $(VENV_DIR)/bin/activate
	$(PY) $(DJANGO_MANAGE) runserver

.PHONY: seed
run: $(PY) $(DJANGO_MANAGE) seed_users

.PHONY: run-prod
run-prod: $(VENV_DIR)/bin/activate collectstatic
	# Example gunicorn command for local prod testing
	$(PY) -m pip install gunicorn --quiet || true
	gunicorn $(PROJECT_NAME).wsgi:application --bind 0.0.0.0:8000 --workers 3

.PHONY: makemigrations
makemigrations: $(VENV_DIR)/bin/activate
	$(PY) $(DJANGO_MANAGE) makemigrations

.PHONY: migrate
migrate: $(VENV_DIR)/bin/activate
	$(PY) $(DJANGO_MANAGE) migrate

.PHONY: createsuperuser
createsuperuser: $(VENV_DIR)/bin/activate
	$(PY) $(DJANGO_MANAGE) createsuperuser

.PHONY: collectstatic
collectstatic: $(VENV_DIR)/bin/activate
	$(PY) $(DJANGO_MANAGE) collectstatic --noinput

# ---------------------------
# Testing & quality
# ---------------------------
.PHONY: test
test: $(VENV_DIR)/bin/activate
	@if command -v pytest >/dev/null 2>&1; then \
	  pytest -q; \
	else \
	  $(PY) $(DJANGO_MANAGE) test; \
	fi

.PHONY: lint
lint: $(VENV_DIR)/bin/activate
	@echo "Formatting with isort + black..."
	@if command -v isort >/dev/null 2>&1; then isort . ; else echo "isort not installed"; fi
	@if command -v black >/dev/null 2>&1; then black . ; else echo "black not installed"; fi
	@echo "Running flake8..."
	@if command -v flake8 >/dev/null 2>&1; then flake8 ; else echo "flake8 not installed"; fi

.PHONY: safety
safety: $(VENV_DIR)/bin/activate
	@if command -v safety >/dev/null 2>&1; then safety check; else echo "safety not installed"; fi

# ---------------------------
# Docker & deployment
# ---------------------------
.PHONY: docker-build
docker-build:
	$(DOCKER) build -t $(DOCKER_IMAGE) .
	@echo "Tagged image as $(DOCKER_IMAGE)"

.PHONY: docker-tag
docker-tag:
	@if [ -z "$(DOCKER_TAG)" ]; then echo "DOCKER_TAG is required"; exit 1; fi
	$(DOCKER) tag $(DOCKER_IMAGE) $(DOCKER_TAG)
	@echo "Tagged $(DOCKER_IMAGE) -> $(DOCKER_TAG)"

.PHONY: docker-push
docker-push: docker-tag
	$(DOCKER) push $(DOCKER_TAG)

.PHONY: compose-up-dev
compose-up-dev:
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) up --build

.PHONY: compose-up-prod
compose-up-prod:
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_PROD) up -d --build

.PHONY: compose-down
compose-down:
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) down

# ---------------------------
# Database helpers (postgres example)
# ---------------------------
BACKUP_DIR := backups
DB_CONTAINER ?= db
DB_NAME ?= $(PROJECT_NAME)_db
DB_USER ?= postgres
DB_PASS ?= postgres
DB_HOST ?= localhost
DB_PORT ?= 5432

.PHONY: backup-db
backup-db:
	@mkdir -p $(BACKUP_DIR)
	@echo "Dumping DB to $(BACKUP_DIR)/db-$$(date +%Y%m%d%H%M).sql (local or docker)"
	@if [ -n "$(DB_CONTAINER)" ]; then \
	  $(DOCKER) exec $(DB_CONTAINER) pg_dump -U $(DB_USER) -F c $(DB_NAME) > $(BACKUP_DIR)/db-$$(date +%Y%m%d%H%M).dump || echo "pg_dump inside container failed"; \
	else \
	  pg_dump -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) -F c $(DB_NAME) > $(BACKUP_DIR)/db-$$(date +%Y%m%d%H%M).dump; \
	fi
	@echo "Backup complete."

.PHONY: restore-db
# usage: make restore-db FILE=backups/db-202201010101.dump
restore-db:
	@if [ -z "$(FILE)" ]; then echo "Please provide FILE=path/to/dump"; exit 1; fi
	@if [ -n "$(DB_CONTAINER)" ]; then \
	  cat $(FILE) | $(DOCKER) exec -i $(DB_CONTAINER) pg_restore -U $(DB_USER) -d $(DB_NAME) --clean || echo "restore failed"; \
	else \
	  pg_restore -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) -d $(DB_NAME) --clean $(FILE); \
	fi
	@echo "Restore complete."

# ---------------------------
# Misc helpers
# ---------------------------
.PHONY: clean
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	rm -rf $(VENV_DIR)
	rm -rf $(STATIC_ROOT) build dist *.egg-info

.PHONY: rebuild
rebuild: clean init install migrate collectstatic

.PHONY: show-env
show-env:
	@echo "DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE)"
	@echo "DOCKER_REGISTRY=$(DOCKER_REGISTRY)"
	@echo "DOCKER_TAG=$(DOCKER_TAG)"
