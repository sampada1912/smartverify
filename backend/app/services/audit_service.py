from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.audit import AuditEvent


def record_audit_event(
    db: Session,
    actor_id: str,
    actor_role: str,
    action: str,
    entity_type: str,
    entity_id: str,
    application_id: Optional[str] = None,
    before_state: Optional[str] = None,
    after_state: Optional[str] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = "127.0.0.1"
) -> AuditEvent:
    event = AuditEvent(
        timestamp=datetime.utcnow(),
        actor_id=actor_id,
        actor_role=actor_role,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        application_id=application_id,
        before_state=before_state,
        after_state=after_state,
        details=details,
        ip_address=ip_address
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
