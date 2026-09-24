.PHONY: install install-web install-api dev-web dev-api dev-worker test-api up down compose-config

install: install-web install-api

install-web:
	cd apps/web && npm install

install-api:
	cd apps/api && uv sync --group dev

dev-web:
	cd apps/web && npm run dev

dev-api:
	cd apps/api && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-worker:
	cd apps/api && uv run python -m app.jobs.worker

test-api:
	cd apps/api && uv run pytest

up:
	docker compose up --build

down:
	docker compose down

compose-config:
	docker compose config --quiet
