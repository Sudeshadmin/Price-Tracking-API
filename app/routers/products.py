from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.cache import cache_get, cache_set
from app.core.database import get_db
from app.models.price_history import PriceHistory
from app.models.product import Product
from app.schemas.product import PriceHistoryOut, ProductOut

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(
    retailer: str | None = Query(default=None, description="Filter by retailer, e.g. 'walmart'"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Paginated product listing. Cached in Redis for a short TTL since this is the
    highest-traffic read endpoint and product data doesn't need to be real-time-fresh.
    """
    cache_key = f"products:retailer={retailer}:limit={limit}:offset={offset}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    query = db.query(Product)
    if retailer:
        query = query.filter(Product.retailer == retailer)
    products = query.order_by(Product.id).offset(offset).limit(limit).all()

    result = [ProductOut.model_validate(p).model_dump(mode="json") for p in products]
    cache_set(cache_key, result)
    return result


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/{product_id}/price-history", response_model=list[PriceHistoryOut])
def get_price_history(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    history = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.recorded_at.desc())
        .all()
    )
    return history
