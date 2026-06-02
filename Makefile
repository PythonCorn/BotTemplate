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

# =========================
# Help
# =========================

.PHONY: help
help:
	@echo "Available commands:"
	@echo ""
	@echo "  make install        Install production dependencies"
	@echo "  make install-dev    Install development dependencies"
	@echo "  make run            Run FastAPI app locally"
	@echo "  make lint           Run ruff linter"
	@echo "  make lint-fix       Run ruff linter with autofix"
	@echo "  make format         Format code with ruff"
	@echo "  make type           Run mypy"
	@echo "  make test           Run tests"
	@echo "  make check          Run lint, type and tests"
	@echo "  make pre-commit     Run pre-commit hooks"
	@echo "  make migrate        Apply Alembic migrations"
	@echo "  make revision       Create Alembic migration, use: make revision m='message'"
	@echo "  make downgrade      Downgrade one Alembic revision"
	@echo "  make clean          Remove cache files"
	@echo ""

# =========================
# Install
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
# App
# =========================

.PHONY: run
run:
	uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT) --reload

# =========================
# Code quality
# =========================

.PHONY: lint
lint:
	ruff check $(APP_DIR)

.PHONY: lint-fix
lint-fix:
	ruff check $(APP_DIR) --fix

.PHONY: format
format:
	ruff format $(APP_DIR)

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
# Alembic
# =========================

.PHONY: migrate
migrate:
	alembic upgrade head

.PHONY: revision
revision:
	alembic revision --autogenerate -m "$(m)"

.PHONY: downgrade
downgrade:
	alembic downgrade -1

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
