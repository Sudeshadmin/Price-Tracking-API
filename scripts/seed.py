"""
Seeds the database with sample products and price history for local testing/demo.
Run with: python -m scripts.seed
"""

from datetime import datetime, timedelta

from app.core.database import Base, SessionLocal, engine
from app.models.price_history import PriceHistory
from app.models.product import Product

Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()
    try:
        if db.query(Product).count() > 0:
            print("Products already exist, skipping seed.")
            return

        sample_products = [
            Product(name="Wireless Mouse", retailer="walmart", url="https://walmart.com/p/1", current_price=19.99),
            Product(name="Wireless Mouse", retailer="sams_club", url="https://samsclub.com/p/1", current_price=17.49),
            Product(name="Mechanical Keyboard", retailer="walmart", url="https://walmart.com/p/2", current_price=59.99),
            Product(name="USB-C Hub", retailer="webstaurantstore", url="https://webstaurantstore.com/p/3", current_price=24.99),
        ]
        db.add_all(sample_products)
        db.commit()

        for product in sample_products:
            db.refresh(product)
            base_price = product.current_price
            for days_ago in range(10, 0, -1):
                db.add(
                    PriceHistory(
                        product_id=product.id,
                        price=round(base_price * (1 + (days_ago % 3) * 0.02), 2),
                        recorded_at=datetime.utcnow() - timedelta(days=days_ago),
                    )
                )
        db.commit()
        print(f"Seeded {len(sample_products)} products with price history.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
