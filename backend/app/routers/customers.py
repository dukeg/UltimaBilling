from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..deps import get_current_user
from ..services.audit import record
from .. import models, schemas

router = APIRouter(prefix="/customers", tags=["customers"])

@router.get("", response_model=list[schemas.CustomerOut])
def list_customers(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.Customer).filter(models.Customer.organization_id == user.organization_id).order_by(models.Customer.id.desc()).all()

@router.post("", response_model=schemas.CustomerOut)
def create_customer(payload: schemas.CustomerCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    customer = models.Customer(organization_id=user.organization_id, **payload.model_dump())
    db.add(customer); db.flush()
    record(db, user.organization_id, user.id, "customer.created", "customer", str(customer.id), customer.name)
    db.commit(); db.refresh(customer)
    return customer
