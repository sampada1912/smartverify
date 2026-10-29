import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class FindingCategory(str, enum.Enum):
    MISSING_DOCUMENT = "MISSING_DOCUMENT"
    MISSING_FIELD = "MISSING_FIELD"
    INVALID_DATE = "INVALID_DATE"
    EXPIRED_DOCUMENT = "EXPIRED_DOCUMENT"
    ID_MISMATCH = "ID_MISMATCH"
    REFERENCE_CONFLICT = "REFERENCE_CONFLICT"
    FIELD_MISMATCH = "FIELD_MISMATCH"
    INSTITUTIONAL_RECORD_MISMATCH = "INSTITUTIONAL_RECORD_MISMATCH"
    INTAKE_INCONSISTENCY = "INTAKE_INCONSISTENCY"
    DUPLICATE_DOCUMENT = "DUPLICATE_DOCUMENT"
    ANOMALY = "ANOMALY"


class FindingSeverity(str, enum.Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class FindingStatus(str, enum.Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    REQUESTED_INFORMATION = "REQUESTED_INFORMATION"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"


class ValidationFinding(Base):
    __tablename__ = "validation_findings"

    id = Column(String(50), primary_key=True, index=True) # e.g. FIND-2026-001
    application_id = Column(String(50), ForeignKey("applications.id"), nullable=False, index=True)
    document_id = Column(String(50), ForeignKey("documents.id"), nullable=True, index=True)
    
    category = Column(Enum(FindingCategory), nullable=False, index=True)
    severity = Column(Enum(FindingSeverity), default=FindingSeverity.MEDIUM, nullable=False, index=True)
    status = Column(Enum(FindingStatus), default=FindingStatus.OPEN, nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    expected_value = Column(String(500), nullable=True)
    observed_value = Column(String(500), nullable=True)
    source_record = Column(String(255), nullable=True)
    page_number = Column(Integer, nullable=True)
    evidence_snippet = Column(Text, nullable=True)
    recommended_action = Column(Text, nullable=False)
    
    # Reviewer actions / overrides
    resolution_notes = Column(Text, nullable=True)
    override_reason = Column(Text, nullable=True)
    resolved_by = Column(String(100), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    detection_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    application = relationship("Application", back_populates="findings")
    document = relationship("Document", back_populates="findings")
