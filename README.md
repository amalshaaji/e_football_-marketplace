# eFootball Account Marketplace

Web platform for browsing, listing, buying, and managing eFootball game accounts.

**Current phase:** 13 — Notifications & Background Jobs (next)

**Completed:** Phase 1 — Foundation; Phase 2 — Frontend Design System; Phase 3 — Database Architecture (models/migration implemented; live DB application pending); Phase 4 — FastAPI Backend Foundation.

Phase status is tracked against the completion criteria in the PRD. Phases 5–12
have initial implementations for authentication, profiles, listings, orders,
buyer/seller dashboards, favorites, reviews, and messaging. These phases remain
in progress pending live PostgreSQL integration. Phase 9 also requires selecting
and verifying a real payment provider. Later phases cover notifications and
background jobs, moderation, security hardening, QA, deployment, operations,
and launch readiness.

Phase 12 implementation is complete: favorites, eligible reviews and
moderation, reporting, participant-only messaging, read state, and user-visible
in-app notifications are implemented. Live PostgreSQL integration has not yet
been verified in this environment.

## Stack

- Frontend: React + Vite (`apps/web`)
- Backend: FastAPI (`apps/api`)
- Database: PostgreSQL
- Architecture: modular monolith

## Prerequisites

- Node.js 22+
- Python 3.11+ (3.12 recommended; Docker uses 3.12)
- [uv](https://docs.astral.sh/uv/)
- Docker Desktop (for PostgreSQL and full compose stack)

## Quick start

```bash
cp .env.example .env
make install
docker compose up postgres -d
make test-api
make dev-api
make dev-web
```

- Web: http://localhost:5173
- API health: http://localhost:8000/health
- API docs: http://localhost:8000/docs

## Commands

| Command | Purpose |
|---|---|
| `make install` | Install frontend and backend dependencies |
| `make dev-web` | Run the Vite dev server |
| `make dev-api` | Run FastAPI with reload |
| `make test-api` | Run backend tests |
| `cd apps/api && uv run alembic upgrade head` | Apply database migrations |
| `cd apps/web && npm run build` | Build the web app |
| `cd apps/web && npm run lint` | Lint the web app |
| `make up` | Build and run the full Docker Compose stack |
| `make down` | Stop Compose services |
| `make compose-config` | Validate Docker Compose configuration |

## Repository layout

```text
apps/web          React + Vite frontend
apps/api          FastAPI backend, SQLAlchemy, Alembic
database/seeds    Future seed data
infrastructure    Docker-related assets
prd               Product requirements
```

Phase 1 does not include authentication, listings, orders, or payments. Phase 2
provides the reusable visual system and navigable page shells only.
