import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class EvidenceRequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    RESPONDED = "RESPONDED"
    CLOSED = "CLOSED"


class EvidenceRequest(Base):
    __tablename__ = "evidence_requests"

    id = Column(String(50), primary_key=True, index=True) # e.g. REQ-2026-001
    application_id = Column(String(50), ForeignKey("applications.id"), nullable=False, index=True)
    finding_id = Column(String(50), ForeignKey("validation_findings.id"), nullable=True, index=True)
    
    requested_by = Column(String(100), nullable=False) # Reviewer username or email
    request_text = Column(Text, nullable=False)
    status = Column(Enum(EvidenceRequestStatus), default=EvidenceRequestStatus.PENDING, nullable=False)
    
    response_text = Column(Text, nullable=True)
    response_document_id = Column(String(50), ForeignKey("documents.id"), nullable=True)
    
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    responded_at = Column(DateTime, nullable=True)

    # Relationships
    application = relationship("Application", back_populates="evidence_requests")
