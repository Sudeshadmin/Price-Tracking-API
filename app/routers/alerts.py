from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.alert import Alert
from app.models.product import Product
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.alert import AlertCreate, AlertOut

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("", response_model=AlertOut, status_code=201)
def create_alert(
    payload: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    alert = Alert(
        user_id=current_user.id,
        product_id=payload.product_id,
        target_price=payload.target_price,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.get("", response_model=list[AlertOut])
def list_my_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Alert).filter(Alert.user_id == current_user.id).all()


@router.delete("/{alert_id}", status_code=204)
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id, Alert.user_id == current_user.id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()
