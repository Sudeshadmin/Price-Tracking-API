from sqlalchemy import Column, DateTime, Float, Index, Integer, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    retailer = Column(String, nullable=False, index=True)  # e.g. "walmart", "sams_club"
    url = Column(String, nullable=False)
    current_price = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    price_history = relationship(
        "PriceHistory", back_populates="product", cascade="all, delete-orphan"
    )
    alerts = relationship("Alert", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        # common real query pattern: "all products for retailer X" — composite index helps it
        Index("ix_products_retailer_name", "retailer", "name"),
    )
