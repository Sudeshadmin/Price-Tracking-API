"""
Background worker: checks all un-triggered alerts against current product prices,
and pushes a notification job onto a Redis queue when a target price is hit.

This is intentionally decoupled from the API request/response cycle — the API layer
never blocks on this work (see the load balancer / queue discussion: this worker is
a "consumer" that pulls jobs at its own pace, not something a client waits on).

Run it as a separate process/container from the API:
    python -m app.worker
"""

import time

from app.core.cache import redis_client
from app.core.database import SessionLocal
from app.models.alert import Alert
from app.models.product import Product

NOTIFICATION_QUEUE_KEY = "notifications"
POLL_INTERVAL_SECONDS = 30


def check_alerts_once() -> int:
    """Runs a single pass over all un-triggered alerts. Returns count of alerts triggered."""
    db = SessionLocal()
    triggered_count = 0
    try:
        alerts = db.query(Alert).filter(Alert.is_triggered.is_(False)).all()
        for alert in alerts:
            product = db.query(Product).filter(Product.id == alert.product_id).first()
            if product and product.current_price <= alert.target_price:
                alert.is_triggered = True
                db.add(alert)

                # Push a notification job for a separate notifier process to send
                # (email/SMS/webhook) — this worker's only job is detection, not delivery.
                job = {
                    "alert_id": alert.id,
                    "user_id": alert.user_id,
                    "product_id": product.id,
                    "product_name": product.name,
                    "target_price": alert.target_price,
                    "current_price": product.current_price,
                }
                redis_client.rpush(NOTIFICATION_QUEUE_KEY, str(job))
                triggered_count += 1

        db.commit()
    finally:
        db.close()

    return triggered_count


def run_forever():
    print("Alert worker started, polling every", POLL_INTERVAL_SECONDS, "seconds")
    while True:
        count = check_alerts_once()
        if count:
            print(f"Triggered {count} alert(s)")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_forever()
