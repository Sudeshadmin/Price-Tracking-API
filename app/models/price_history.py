from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    product = relationship("Product", back_populates="price_history")
