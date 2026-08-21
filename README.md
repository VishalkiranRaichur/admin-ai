# Admin AI

AI-powered operating system for startups and small companies. Upload internal documents, ask business questions in natural language, and get insights backed by source citations.

## Stack

- **Frontend:** Next.js 15, TypeScript, Tailwind CSS, Clerk auth
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL + pgvector
- **Infrastructure:** Redis, MinIO (S3-compatible), Celery (Phase 1+)

## Project structure

```
admin-ai/
├── apps/
│   ├── web/          # Next.js frontend
│   └── api/          # FastAPI backend
├── workers/
│   └── celery/       # Async job workers (Phase 1+)
├── infra/
│   └── docker-compose.yml
└── .github/workflows/ci.yml
```

## Prerequisites

- Node.js 20+
- Python 3.11+
- Docker & Docker Compose

## Quick start

### 1. Start infrastructure

```bash
make infra-up
# or: docker compose -f infra/docker-compose.yml up -d
```

Services:
| Service  | URL                    | Credentials        |
|----------|------------------------|--------------------|
| Postgres | localhost:5432         | adminai / adminai  |
| Redis    | localhost:6379         | —                  |
| MinIO    | localhost:9000 (API)   | minioadmin / minioadmin |
| MinIO UI | localhost:9001         | minioadmin / minioadmin |

### 2. Configure environment

```bash
cp apps/web/.env.example apps/web/.env.local
cp apps/api/.env.example apps/api/.env
```

Add your [Clerk](https://dashboard.clerk.com) keys to `apps/web/.env.local`.

### 3. Install dependencies

```bash
make install
```

### 4. Initialize the database schema

For a fresh database:

```bash
make db-upgrade
```

For an existing local database created before Alembic was added, validate and
stamp the document schema before applying additive migrations:

```bash
make db-baseline
make db-upgrade
```

The baseline command refuses to stamp partial or drifted schemas.

### 5. Run the apps

Terminal 1 — API:
```bash
make dev-api
```

Terminal 2 — Web:
```bash
make dev
```

- Web: http://localhost:3000
- API: http://localhost:8000
- API docs: http://localhost:8000/docs

## Development

```bash
# Run API tests
cd apps/api && .venv/bin/pytest

# Lint API
cd apps/api && .venv/bin/ruff check app tests

# Lint web
cd apps/web && npm run lint
```

## Roadmap

- **Phase 0** (current): Monorepo, Docker, CI, auth, dashboard shell
- **Phase 1**: Document upload + ingestion pipeline
- **Phase 2**: Chat + RAG with citations
- **Phase 3**: Insight generation
- **Phase 4**: Weekly reports + polish
- **Phase 5**: Integrations (Gmail, Slack, Drive, Calendar)
