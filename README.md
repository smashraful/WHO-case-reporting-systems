# WHO Measles Outbreak & Case-Based Reporting — Backend

FastAPI + PostgreSQL backend for measles case surveillance: role-based case
notification → lab results → verification, with Redis-cached summary stats and a
RabbitMQ alert pipeline.

## Stack

- **FastAPI** (API) · **SQLAlchemy 2** + **Alembic** (ORM/migrations) · **PostgreSQL**
- **Redis** (cached dashboard stats) · **RabbitMQ** (async case-event alerts)
- **JWT** auth (access + refresh) with 5 roles · **pytest** + TestClient

## Roles

| Role | Can do |
|------|--------|
| `field_worker` | register patients, file cases |
| `lab_staff` | enter lab results |
| `district_officer` | verify / update case status, view stats |
| `program_manager` | view users & stats (oversight) |
| `admin` | manage users, locations, everything |

## Quick start (Docker)

```bash
cp .env.example .env          # fill in DB_PASSWORD, SECRET_KEY (openssl rand -hex 32), FIRST_ADMIN_PASSWORD
docker compose up --build     # postgres, redis, rabbitmq, api (runs migrations), worker
docker compose exec api python -m app.scripts.seed   # bootstrap admin + locations
```

Services and host ports. Host ports are remapped to avoid clashing with other
local stacks; the container-internal ports (used for service-to-service traffic
over the Docker network) are unchanged:

| Service         | Reach it on the host                    | Container port |
|-----------------|-----------------------------------------|----------------|
| API (FastAPI)   | http://localhost:8000/docs              | 8000           |
| PostgreSQL      | `localhost:5433`                        | 5432           |
| Redis           | `localhost:6380`                        | 6379           |
| RabbitMQ (AMQP) | `localhost:5673`                        | 5672           |
| RabbitMQ UI     | http://localhost:15673 (guest/guest)    | 15672          |

> Keep `DB_PORT=5432` in `.env`: the API and worker connect to Postgres over the
> Docker network using the container port. The host ports above are only for
> connecting from your own machine (psql, a Redis GUI, the RabbitMQ UI, …).

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in secrets; point DB_* at a local Postgres
alembic upgrade head          # apply schema
python -m app.scripts.seed    # bootstrap admin + locations
uvicorn app.main:app --reload
python -m app.workers.notifications   # (separate shell) run the alert worker
```

## Key endpoints

- `POST /auth/login` · `POST /auth/refresh` · `GET /auth/me`
- `POST/GET /users` (admin) · `GET/DELETE /users/{id}`
- `GET/POST /locations`
- `GET/POST /patients` · `GET /patients/{id}`
- `GET/POST /cases` · `GET /cases/{id}` · `PATCH /cases/{id}/status` · `GET /cases/stats`
- `GET/POST /cases/{case_id}/lab-results`
- `GET /health` · `GET /health/database`

## Migrations

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## Tests

```bash
pytest            # in-memory SQLite; infra (Redis/RabbitMQ) mocked — no services required
```

## Notes

- `.env` is git-ignored; never commit real secrets. Rotate any credential that
  was previously committed.
- Redis and RabbitMQ degrade gracefully — if unreachable, the API still serves
  requests (stats fall back to live queries; alerts are best-effort).
