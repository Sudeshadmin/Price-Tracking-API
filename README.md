# Price Tracker API

A REST API that tracks product prices across retailers, records price history, and
lets users set price-drop alerts. Built to demonstrate backend engineering fundamentals:
API design, relational modeling, auth, caching, background workers, containerization, and testing.

## Architecture

```
Client → FastAPI (uvicorn) → Postgres (products, users, alerts, price_history)
                            → Redis (cache for GET /products)

Background worker (separate process) → polls Postgres for un-triggered alerts
                                      → pushes notification jobs onto a Redis list
```

The API and the alert-checking worker are **separate processes** (see `docker-compose.yml`).
The API never blocks a request on alert-checking logic — that work happens asynchronously,
on the worker's own schedule. This mirrors the producer/consumer pattern: the API is a
lightweight producer of alert state changes, and a (not-yet-built) notifier service would
consume the `notifications` Redis list to actually send emails/webhooks.

## Why these choices

- **FastAPI over Flask/Django** — native async support, automatic OpenAPI docs, Pydantic
  validation built in, which keeps request/response contracts explicit and type-checked.
- **Postgres over Snowflake/other OLAP stores** — this is an OLTP workload: frequent small
  reads/writes, relational integrity (foreign keys between users/products/alerts) matters,
  and there's no need for analytical column-store performance here.
- **Redis for caching, not as primary storage** — `GET /products` is the highest-traffic
  read; caching it with a short TTL (60s) cuts DB load without risking seriously stale data.
  Cache failures fail open (see `app/core/cache.py`) — Redis being down should degrade
  performance, not take the API down.
- **Separate worker process, not a cron job inside the API** — keeps the request/response
  cycle fast and lets the API and worker scale independently.
- **JWT auth, not session cookies** — stateless, works cleanly for an API consumed by
  multiple clients (web, mobile, scripts) without server-side session storage.

## Project structure

```
app/
  core/       # config, DB session, security (JWT/password hashing), Redis client
  models/     # SQLAlchemy ORM models (User, Product, PriceHistory, Alert)
  schemas/    # Pydantic request/response models
  routers/    # API endpoints, grouped by resource
  main.py     # FastAPI app + router wiring
  worker.py   # background process that checks alerts against current prices
scripts/
  seed.py     # populates sample data for local testing
tests/        # pytest suite, runs against in-memory SQLite (no external deps needed)
```

## Running locally

**With Docker (recommended):**
```bash
docker-compose up --build
```
API available at `http://localhost:8000`, docs at `http://localhost:8000/docs`.

**Without Docker:**
```bash
pip install -r requirements.txt
cp .env.example .env   # edit if needed
uvicorn app.main:app --reload
```

**Seed sample data:**
```bash
python -m scripts.seed
```

**Run the alert worker separately:**
```bash
python -m app.worker
```

**Run tests:**
```bash
pytest tests/ -v
```

## API endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/signup` | — | Create a user |
| POST | `/auth/login` | — | Get a JWT access token |
| GET | `/products` | — | List products, filterable by `retailer`, paginated |
| GET | `/products/{id}` | — | Get a single product |
| GET | `/products/{id}/price-history` | — | Price history for a product |
| POST | `/alerts` | JWT | Create a price-drop alert |
| GET | `/alerts` | JWT | List the current user's alerts |
| DELETE | `/alerts/{id}` | JWT | Delete an alert |

Full interactive docs (Swagger UI) at `/docs` once running.

## What's intentionally not built (out of scope for a portfolio piece)

- Alembic migrations are included but not wired into a full migration history —
  `Base.metadata.create_all` is used for quick local bring-up.
- The notifier service that would actually consume the `notifications` queue and send
  emails is not implemented — the worker only detects and enqueues.
- No rate limiting on endpoints — would add via `slowapi` or an API gateway in production.
