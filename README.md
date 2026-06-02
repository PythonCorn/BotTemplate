# BotTemplate

Production-ready template for Telegram bots based on FastAPI, Aiogram 3, PostgreSQL, Redis and Docker.

## Features

* FastAPI
* Aiogram 3
* PostgreSQL
* Redis
* SQLAlchemy 2.0
* Alembic
* Docker & Docker Compose
* APScheduler Workers
* Webhook support
* GitHub Actions CI
* Ruff
* Mypy
* Pytest

## Project Structure

```text
app/
├── api/               # FastAPI routers
├── bot/               # Telegram bot
├── core/              # Configuration and application state
├── database/          # Database setup
├── infrastructure/    # External integrations
├── repositories/      # Database repositories
├── workers/           # Background workers
└── main.py
```

## Installation

Clone repository:

```bash
git clone https://github.com/PythonCorn/BotTemplate.git
cd BotTemplate
```

Create virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Environment Variables

Create `.env` file:

```env
BOT_TOKEN=
POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

REDIS_HOST=
REDIS_PORT=
REDIS_PASSWORD=
REDIS_DB=
```

## Database

Create migrations:

```bash
alembic revision --autogenerate -m "init"
```

Apply migrations:

```bash
alembic upgrade head
```

## Run Application

Start FastAPI:

```bash
python -m app.main
```

Start Worker:

```bash
python -m app.workers.main
```

## Docker

Build and start containers:

```bash
docker compose up -d --build
```

Stop containers:

```bash
docker compose down
```

## Code Quality

Run Ruff:

```bash
ruff check .
ruff format .
```

Run Mypy:

```bash
mypy app
```

Run Tests:

```bash
pytest
```

## CI

GitHub Actions automatically runs:

* Ruff
* Mypy
* Pytest

for every push and pull request.

## License

MIT
