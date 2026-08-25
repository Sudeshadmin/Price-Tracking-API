import os

from fastapi import FastAPI

from app.core.database import Base, engine
from app.routers import alerts, auth, products

# In production you'd use Alembic migrations instead of create_all — kept here for
# quick local bring-up. Skipped under pytest, where tests wire up their own
# in-memory SQLite schema instead (see tests/conftest.py).
if not os.getenv("PYTEST_CURRENT_TEST") and "PYTEST_RUNNING" not in os.environ:
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Price Tracker API",
    description="Tracks product prices across retailers and alerts users on price drops.",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(alerts.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
