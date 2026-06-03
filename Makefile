# =========================
# Project settings
# =========================

PYTHON := python
PIP := pip

APP_DIR := app
TESTS_DIR := tests
APP_MODULE := app.main:app

HOST := 0.0.0.0
PORT := 8000

COMPOSE := docker compose
COMPOSE_DEV := docker compose -f docker-compose.yml -f docker-compose.dev.yml
COMPOSE_PROD := docker compose -f docker-compose.yml -f docker-compose.prod.yml

ALEMBIC=$(COMPOSE_DEV) exec app alembic -c alembic.ini

# =========================
# Help
# =========================

.PHONY: help
help:
	@echo "Available commands:"
	@echo ""
	@echo "Local:"
	@echo "  make install          Install production dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo "  make run              Run FastAPI app locally"
	@echo "  make worker           Run worker locally"
	@echo ""
	@echo "Code quality:"
	@echo "  make lint             Run ruff linter"
	@echo "  make lint-fix         Run ruff linter with autofix"
	@echo "  make format           Format code with ruff"
	@echo "  make type             Run mypy"
	@echo "  make test             Run tests"
	@echo "  make check            Run lint, type and tests"
	@echo "  make pre-commit       Run pre-commit hooks"
	@echo ""
	@echo "Alembic:"
	@echo "  make migrate          Apply migrations locally"
	@echo "  make revision m='msg' Create migration locally"
	@echo "  make downgrade        Downgrade one revision locally"
	@echo ""
	@echo "Docker dev:"
	@echo "  make dev-up           Start dev containers"
	@echo "  make dev-down         Stop dev containers"
	@echo "  make dev-build        Rebuild dev containers"
	@echo "  make dev-logs         Show dev logs"
	@echo ""
	@echo "Docker prod:"
	@echo "  make prod-up          Start prod containers"
	@echo "  make prod-down        Stop prod containers"
	@echo "  make prod-build       Rebuild prod containers"
	@echo "  make prod-logs        Show prod logs"
	@echo ""
	@echo "Docker tools:"
	@echo "  make app-shell        Open app container shell"
	@echo "  make worker-shell     Open worker container shell"
	@echo "  make app-logs         Show app logs"
	@echo "  make worker-logs      Show worker logs"
	@echo "  make postgres-logs    Show postgres logs"
	@echo "  make redis-logs       Show redis logs"
	@echo "  make migrate-docker   Apply migrations in app container"
	@echo "  make revision-docker m='msg' Create migration in app container"
	@echo ""
	@echo "Cleaning:"
	@echo "  make clean            Remove Python cache files"

# =========================
# Local install
# =========================

.PHONY: install
install:
	$(PIP) install -r requirements.txt

.PHONY: install-dev
install-dev:
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	pre-commit install

# =========================
# Local run
# =========================

.PHONY: run
run:
	uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT) --reload

.PHONY: worker
worker:
	$(PYTHON) -m app.workers.main

# =========================
# Code quality
# =========================

.PHONY: lint
lint:
	ruff check $(APP_DIR) $(TESTS_DIR)

.PHONY: lint-fix
lint-fix:
	ruff check $(APP_DIR) $(TESTS_DIR) --fix

.PHONY: format
format:
	ruff format $(APP_DIR) $(TESTS_DIR)

.PHONY: type
type:
	mypy $(APP_DIR)

.PHONY: test
test:
	pytest $(TESTS_DIR)

.PHONY: check
check: lint type test

.PHONY: pre-commit
pre-commit:
	pre-commit run --all-files

# =========================
# Alembic local
# =========================

.PHONY: migrate
migrate:
	$(ALEMBIC) upgrade head

.PHONY: revision
revision:
	$(ALEMBIC) revision --autogenerate -m "$(m)"

.PHONY: downgrade
downgrade:
	$(ALEMBIC) downgrade -1

docker-clean:
	docker system prune -af

# =========================
# Docker dev
# =========================

.PHONY: dev-up
dev-up:
	$(COMPOSE_DEV) up -d --build

.PHONY: dev-down
dev-down:
	$(COMPOSE_DEV) down --remove-orphans
	docker image prune -f

.PHONY: dev-build
dev-build:
	$(COMPOSE_DEV) build --no-cache

.PHONY: dev-restart
dev-restart:
	$(COMPOSE_DEV) restart

.PHONY: dev-logs
dev-logs:
	$(COMPOSE_DEV) logs -f

# =========================
# Docker prod
# =========================

.PHONY: prod-up
prod-up:
	$(COMPOSE_PROD) up -d --build

.PHONY: prod-down
prod-down:
	$(COMPOSE_PROD) down

.PHONY: prod-build
prod-build:
	$(COMPOSE_PROD) build --no-cache

.PHONY: prod-restart
prod-restart:
	$(COMPOSE_PROD) restart

.PHONY: prod-logs
prod-logs:
	$(COMPOSE_PROD) logs -f

# =========================
# Docker service logs
# =========================

.PHONY: app-logs
app-logs:
	$(COMPOSE) logs -f app

.PHONY: worker-logs
worker-logs:
	$(COMPOSE) logs -f worker

.PHONY: postgres-logs
postgres-logs:
	$(COMPOSE) logs -f postgres

.PHONY: redis-logs
redis-logs:
	$(COMPOSE) logs -f redis

# =========================
# Docker shell
# =========================

.PHONY: app-shell
app-shell:
	$(COMPOSE) exec app bash

.PHONY: worker-shell
worker-shell:
	$(COMPOSE) exec worker bash

.PHONY: postgres-shell
postgres-shell:
	$(COMPOSE) exec postgres psql -U $${POSTGRES_USER} -d $${POSTGRES_DB}

.PHONY: redis-shell
redis-shell:
	$(COMPOSE) exec redis redis-cli

# =========================
# Alembic docker
# =========================

.PHONY: migrate-docker
migrate-docker:
	$(COMPOSE) exec app alembic upgrade head

.PHONY: revision-docker
revision-docker:
	$(COMPOSE) exec app alembic revision --autogenerate -m "$(m)"

.PHONY: downgrade-docker
downgrade-docker:
	$(COMPOSE) exec app alembic downgrade -1

# =========================
# Cleaning
# =========================

.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
