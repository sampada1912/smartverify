import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class ComplianceStatus(str, enum.Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class ComplianceRuleSeverity(str, enum.Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. R-AICTE-EOA-FAC-01
    rule_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category_condition = Column(String(100), default="ALL", nullable=False) # EXTENSION_OF_APPROVAL, ALL
    required_evidence_type = Column(String(100), nullable=False) # FACULTY_LIST, NOC, etc.
    evaluation_logic = Column(String(100), nullable=False) # e.g. FACULTY_CADRE_RATIO, NOC_VALIDITY, LAND_AREA_RATIO
    severity = Column(Enum(ComplianceRuleSeverity), default=ComplianceRuleSeverity.HIGH, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    version = Column(String(20), default="2026.1-ILLUSTRATIVE")
    effective_date = Column(String(50), default="2026-01-01")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ComplianceEvaluation(Base):
    __tablename__ = "compliance_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String(50), ForeignKey("applications.id"), nullable=False, index=True)
    rule_id = Column(String(50), nullable=False, index=True)
    rule_name = Column(String(255), nullable=False)
    status = Column(Enum(ComplianceStatus), default=ComplianceStatus.NEEDS_REVIEW, nullable=False)
    explanation = Column(Text, nullable=False)
    evidence_summary = Column(Text, nullable=True)
    evaluated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    application = relationship("Application", back_populates="compliance_evaluations")
