from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..deps import get_current_user
from ..services.audit import record
from .. import models, schemas

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.get("")
def list_subscriptions(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.Subscription).filter_by(organization_id=user.organization_id).order_by(models.Subscription.id.desc()).all()

@router.post("")
def create_subscription(payload: schemas.SubscriptionCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    if not db.query(models.Customer).filter_by(id=payload.customer_id, organization_id=user.organization_id).first():
        raise HTTPException(404, "Customer not found")
    sub = models.Subscription(organization_id=user.organization_id, **payload.model_dump())
    db.add(sub); db.flush()
    record(db, user.organization_id, user.id, "subscription.created", "subscription", str(sub.id), sub.name)
    db.commit(); db.refresh(sub)
    return sub

@router.post("/{subscription_id}/cancel")
def cancel_subscription(subscription_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    sub = db.query(models.Subscription).filter_by(id=subscription_id, organization_id=user.organization_id).first()
    if not sub: raise HTTPException(404, "Subscription not found")
    sub.cancel_at_period_end = True; sub.status = "canceling"
    record(db, user.organization_id, user.id, "subscription.canceling", "subscription", str(sub.id), "cancel_at_period_end")
    db.commit()
    return {"status": sub.status}
