from sqlalchemy.orm import Session
from .. import models

def record(db: Session, org_id: int, actor_id: int | None, action: str, entity_type: str, entity_id: str, details: str = ""):
    db.add(models.AuditLog(organization_id=org_id, actor_user_id=actor_id, action=action, entity_type=entity_type, entity_id=entity_id, details=details))
