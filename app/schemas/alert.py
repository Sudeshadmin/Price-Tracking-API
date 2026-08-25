from pydantic import BaseModel


class AlertCreate(BaseModel):
    product_id: int
    target_price: float


class AlertOut(BaseModel):
    id: int
    product_id: int
    target_price: float
    is_triggered: bool

    class Config:
        from_attributes = True
