from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class ChecklistRule(Base):
    __tablename__ = "checklist_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_code = Column(String(50), unique=True, index=True, nullable=False)
    category = Column(String(100), default="ALL", nullable=False) # e.g. EXTENSION_OF_APPROVAL, ALL
    document_type = Column(String(100), nullable=False) # Maps to DocumentType
    requirement_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    is_required = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    version = Column(String(20), default="2026.1-PROTOTYPE")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApplicationChecklistItem(Base):
    __tablename__ = "application_checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String(50), ForeignKey("applications.id"), nullable=False, index=True)
    rule_code = Column(String(50), nullable=False)
    requirement_name = Column(String(255), nullable=False)
    document_type = Column(String(100), nullable=False)
    is_required = Column(Boolean, default=True)
    is_submitted = Column(Boolean, default=False)
    document_id = Column(String(50), ForeignKey("documents.id"), nullable=True)
    validation_status = Column(String(50), default="MISSING") # SATISFIED, MISSING, INCOMPLETE, EXPIRED, MISMATCH
    explanation = Column(Text, nullable=True)
    evidence_summary = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    application = relationship("Application", back_populates="checklist_items")
