# eFootball Account Marketplace

Web platform for browsing, listing, buying, and managing eFootball game accounts.

**Current phase:** 15 — Security Hardening (next)

**Completed:** Phase 1 — Foundation; Phase 2 — Frontend Design System; Phase 3 — Database Architecture (models/migration implemented; live DB application pending); Phase 4 — FastAPI Backend Foundation.

Phase status is tracked against the completion criteria in the PRD. Phases 5–12
have initial implementations for authentication, profiles, listings, orders,
buyer/seller dashboards, favorites, reviews, and messaging. These phases remain
in progress pending live PostgreSQL integration. Phase 9 also requires selecting
and verifying a real payment provider. Later phases cover admin moderation,
security hardening, QA, deployment, operations, and launch readiness.

Phase 12 implementation is complete: favorites, eligible reviews and
moderation, reporting, participant-only messaging, read state, and user-visible
in-app notifications are implemented. Live PostgreSQL integration has not yet
been verified in this environment.

Phase 13 adds a Redis-backed worker queue with processing recovery, retries,
dead-letter handling, async notification persistence, and expired-checkout
cleanup. SMTP email delivery and safe image metadata processing are supported
when configured. Image resizing and remote storage upload remain unimplemented.
The worker and Redis configuration are in Compose; live Redis/database worker
integration has not been run in this environment.

After registering a trusted account, an operator can bootstrap an administrator
from `apps/api` with `uv run python scripts/set_admin_role.py user@example.com`.

Phase 14 implements administrator-only user management, listing and report
moderation, review controls, order/payment inspection, platform statistics, and
audit history. Live database verification remains pending.

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
docker compose up postgres redis -d
make test-api
make dev-api
make dev-worker
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
| `make dev-worker` | Run the Redis-backed job worker |
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
