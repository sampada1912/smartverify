import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class ApplicationCategory(str, enum.Enum):
    EXTENSION_OF_APPROVAL = "EXTENSION_OF_APPROVAL"
    INCREASE_IN_INTAKE = "INCREASE_IN_INTAKE"
    NEW_INSTITUTION = "NEW_INSTITUTION"
    NEW_PROGRAMME = "NEW_PROGRAMME"


class ApplicationStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_SCRUTINY = "UNDER_SCRUTINY"
    DEFICIENCIES_COMMUNICATED = "DEFICIENCIES_COMMUNICATED"
    PENDING_REVIEW = "PENDING_REVIEW"
    SCRUTINY_COMPLETED = "SCRUTINY_COMPLETED"


class ValidationOverallStatus(str, enum.Enum):
    NOT_EVALUATED = "NOT_EVALUATED"
    CLEAN = "CLEAN"
    DEFICIENCIES_DETECTED = "DEFICIENCIES_DETECTED"
    HIGH_RISK = "HIGH_RISK"


class Application(Base):
    __tablename__ = "applications"

    id = Column(String(50), primary_key=True, index=True)
    institution_id = Column(String(100), index=True, nullable=False)
    institution_name = Column(String(255), index=True, nullable=False)
    category = Column(Enum(ApplicationCategory), default=ApplicationCategory.EXTENSION_OF_APPROVAL, nullable=False)
    academic_year = Column(String(20), default="2026-27", nullable=False)
    programme = Column(String(100), default="ENGINEERING_AND_TECHNOLOGY", nullable=False)
    course_name = Column(String(255), default="Computer Science and Engineering", nullable=False)
    existing_intake = Column(Integer, default=120, nullable=False)
    requested_intake = Column(Integer, default=180, nullable=False)
    
    contact_person = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=False)
    
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.DRAFT, nullable=False)
    validation_status = Column(Enum(ValidationOverallStatus), default=ValidationOverallStatus.NOT_EVALUATED, nullable=False)
    
    assigned_reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    submission_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="application", cascade="all, delete-orphan")
    checklist_items = relationship("ApplicationChecklistItem", back_populates="application", cascade="all, delete-orphan")
    findings = relationship("ValidationFinding", back_populates="application", cascade="all, delete-orphan")
    compliance_evaluations = relationship("ComplianceEvaluation", back_populates="application", cascade="all, delete-orphan")
    verification_results = relationship("VerificationResult", back_populates="application", cascade="all, delete-orphan")
    evidence_requests = relationship("EvidenceRequest", back_populates="application", cascade="all, delete-orphan")
