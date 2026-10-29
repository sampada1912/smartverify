import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class VerificationStatus(str, enum.Enum):
    VERIFIED = "VERIFIED"
    MISMATCH_DETECTED = "MISMATCH_DETECTED"
    EXPIRED = "EXPIRED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    VERIFICATION_PENDING = "VERIFICATION_PENDING"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"


class MockAuthorityRecord(Base):
    """Synthetic authoritative records repository for demonstration verification only."""
    __tablename__ = "mock_authority_records"

    id = Column(Integer, primary_key=True, index=True)
    authority_name = Column(String(100), index=True, nullable=False) # e.g. STATE_TECHNICAL_BOARD_MOCK
    certificate_number = Column(String(100), index=True, nullable=False)
    institution_id = Column(String(100), index=True, nullable=False)
    institution_name = Column(String(255), nullable=False)
    doc_type = Column(String(100), nullable=False)
    issue_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)
    status = Column(String(50), default="VALID", nullable=False) # VALID, REVOKED, EXPIRED, SUSPENDED
    details_json = Column(Text, nullable=True)
    is_simulated = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class VerificationResult(Base):
    __tablename__ = "verification_results"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String(50), ForeignKey("applications.id"), nullable=False, index=True)
    document_id = Column(String(50), ForeignKey("documents.id"), nullable=True, index=True)
    
    authority_name = Column(String(100), nullable=False)
    certificate_number = Column(String(100), nullable=False)
    status = Column(Enum(VerificationStatus), default=VerificationStatus.VERIFICATION_PENDING, nullable=False)
    is_simulated = Column(Boolean, default=True, nullable=False)
    check_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    mismatch_details = Column(Text, nullable=True)
    raw_response_json = Column(Text, nullable=True)
    
    # Relationships
    application = relationship("Application", back_populates="verification_results")
