# Daladala Live

A FastAPI application for managing daladala (public transport) live tracking data.

## Commands

```bash
poetry install
poetry run alembic init alembic
poetry run alembic revision --autogenerate -m "Add vehicles and vehicles_users tables"
poetry run alembic upgrade head
```

## Run the application

```bash
poetry run uvicorn volta_api.main:app --reload --app-dir src
```
