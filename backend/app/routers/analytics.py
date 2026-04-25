from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..deps import get_current_user
from .. import models

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary")
def summary(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    q = db.query(models.Invoice).filter_by(organization_id=user.organization_id)
    revenue = db.query(func.coalesce(func.sum(models.Invoice.total), 0)).filter_by(organization_id=user.organization_id, status="paid").scalar()
    outstanding = db.query(func.coalesce(func.sum(models.Invoice.total), 0)).filter(models.Invoice.organization_id == user.organization_id, models.Invoice.status != "paid").scalar()
    return {"invoices": q.count(), "paid_revenue": revenue, "outstanding": outstanding, "customers": db.query(models.Customer).filter_by(organization_id=user.organization_id).count(), "subscriptions": db.query(models.Subscription).filter_by(organization_id=user.organization_id).count()}
