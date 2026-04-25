from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import verify_password, create_access_token, get_password_hash
from .. import models, schemas

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_access_token(user.email, user.role, user.organization_id), "role": user.role}

@router.post("/bootstrap")
def bootstrap(db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == "admin@example.com").first():
        return {"status": "already_seeded"}
    org = models.Organization(name="Demo Organization", billing_email="admin@example.com")
    db.add(org); db.flush()
    db.add(models.User(organization_id=org.id, full_name="Admin User", email="admin@example.com", password_hash=get_password_hash("Admin@12345"), role="owner"))
    db.commit()
    return {"status": "seeded", "email": "admin@example.com", "password": "Admin@12345"}
