from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from app.database import Base


class SyntheticInstitutionRecord(Base):
    """Synthetic baseline institutional records used to cross-reference application data."""
    __tablename__ = "synthetic_institution_records"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(String(100), unique=True, index=True, nullable=False)
    institution_name = Column(String(255), index=True, nullable=False)
    approved_academic_year = Column(String(20), default="2025-26", nullable=False)
    approved_programme = Column(String(100), default="ENGINEERING_AND_TECHNOLOGY", nullable=False)
    approved_course = Column(String(255), default="Computer Science and Engineering", nullable=False)
    approved_intake = Column(Integer, default=120, nullable=False)
    
    land_area_acres = Column(Float, default=5.0, nullable=False)
    built_up_area_sqm = Column(Float, default=12500.0, nullable=False)
    affiliating_university = Column(String(255), default="Dr. A.P.J. Abdul Kalam Technical University", nullable=False)
    state = Column(String(100), default="Uttar Pradesh", nullable=False)
    
    is_synthetic: bool = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
