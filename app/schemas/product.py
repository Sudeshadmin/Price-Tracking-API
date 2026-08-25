from datetime import datetime

from pydantic import BaseModel


class ProductOut(BaseModel):
    id: int
    name: str
    retailer: str
    url: str
    current_price: float
    currency: str
    updated_at: datetime

    class Config:
        from_attributes = True


class PriceHistoryOut(BaseModel):
    price: float
    recorded_at: datetime

    class Config:
        from_attributes = True
