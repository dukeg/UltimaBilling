from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..deps import require_roles
from ..core.security import get_password_hash
from ..services.audit import record
from .. import models, schemas

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users")
def users(db: Session = Depends(get_db), user: models.User = Depends(require_roles("owner", "admin"))):
    return db.query(models.User).filter_by(organization_id=user.organization_id).all()

@router.post("/users")
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db), user: models.User = Depends(require_roles("owner", "admin"))):
    new = models.User(organization_id=user.organization_id, full_name=payload.full_name, email=payload.email, password_hash=get_password_hash(payload.password), role=payload.role)
    db.add(new); db.flush(); record(db, user.organization_id, user.id, "user.created", "user", str(new.id), payload.email); db.commit(); return new

@router.get("/audit-logs")
def audit_logs(db: Session = Depends(get_db), user: models.User = Depends(require_roles("owner", "admin"))):
    return db.query(models.AuditLog).filter_by(organization_id=user.organization_id).order_by(models.AuditLog.id.desc()).limit(100).all()
