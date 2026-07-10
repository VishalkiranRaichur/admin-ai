.PHONY: dev dev-api infra-up infra-down install-api install-web

install-web:
	cd apps/web && npm install

install-api:
	cd apps/api && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

install: install-web install-api

infra-up:
	docker compose -f infra/docker-compose.yml up -d

infra-down:
	docker compose -f infra/docker-compose.yml down

dev-api:
	cd apps/api && .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev:
	cd apps/web && npm run dev
