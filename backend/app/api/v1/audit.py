from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.user import User, UserRole
from app.models.application import Application
from app.models.audit import AuditEvent
from app.schemas.audit import AuditEventResponse
from app.services.auth_service import get_current_user, verify_application_access

router = APIRouter(tags=["Audit Trail"])


@router.get("/audit", response_model=List[AuditEventResponse])
def search_audit_trail(
    application_id: Optional[str] = None,
    action: Optional[str] = None,
    actor_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(AuditEvent)

    if current_user.role == UserRole.INSTITUTION:
        # Retrieve IDs of applications belonging to this institution
        inst_apps = db.query(Application.id).filter(Application.institution_id == current_user.institution_id).all()
        inst_app_ids = [a[0] for a in inst_apps]

        if application_id:
            verify_application_access(application_id, db, current_user)
            query = query.filter(AuditEvent.application_id == application_id)
        else:
            query = query.filter(
                (AuditEvent.application_id.in_(inst_app_ids)) |
                (AuditEvent.actor_id == current_user.username)
            )
    else:
        if application_id:
            query = query.filter(AuditEvent.application_id == application_id)

    if action:
        query = query.filter(AuditEvent.action == action)
    if actor_id:
        query = query.filter(AuditEvent.actor_id == actor_id)
    if entity_type:
        query = query.filter(AuditEvent.entity_type == entity_type)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            AuditEvent.details.ilike(search_pattern) |
            AuditEvent.actor_id.ilike(search_pattern) |
            AuditEvent.action.ilike(search_pattern) |
            AuditEvent.application_id.ilike(search_pattern)
        )

    events = query.order_by(desc(AuditEvent.timestamp)).offset(skip).limit(limit).all()
    return events
