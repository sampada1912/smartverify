from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    actor_id = Column(String(100), nullable=False, index=True) # e.g. "reviewer1" or "SYSTEM_AI_ENGINE"
    actor_role = Column(String(50), nullable=False) # "REVIEWER", "INSTITUTION", "ADMIN", "SYSTEM"
    action = Column(String(100), nullable=False, index=True) # e.g. "APPLICATION_SUBMITTED", "FIELD_CORRECTED"
    
    entity_type = Column(String(50), nullable=False, index=True) # "APPLICATION", "DOCUMENT", "FINDING", "RULE"
    entity_id = Column(String(100), nullable=False, index=True)
    application_id = Column(String(50), nullable=True, index=True)
    
    before_state = Column(Text, nullable=True) # JSON or descriptive string
    after_state = Column(Text, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True, default="127.0.0.1")
