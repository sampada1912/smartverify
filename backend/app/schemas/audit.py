from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AuditEventResponse(BaseModel):
    id: int
    timestamp: datetime
    actor_id: str
    actor_role: str
    action: str
    entity_type: str
    entity_id: str
    application_id: Optional[str] = None
    before_state: Optional[str] = None
    after_state: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None

    class Config:
        from_attributes = True


class AuditEventFilter(BaseModel):
    application_id: Optional[str] = None
    action: Optional[str] = None
    actor_id: Optional[str] = None
    entity_type: Optional[str] = None
