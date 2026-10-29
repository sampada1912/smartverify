from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(50), ForeignKey("documents.id"), nullable=False, index=True)
    application_id = Column(String(50), ForeignKey("applications.id"), nullable=False, index=True)
    
    field_name = Column(String(100), index=True, nullable=False)
    extracted_value = Column(String(500), nullable=False)
    normalized_value = Column(String(500), nullable=False)
    page_number = Column(Integer, default=1)
    confidence = Column(Float, default=0.90)
    extraction_method = Column(String(100), default="REGEX_PATTERN")
    snippet = Column(Text, nullable=True)
    
    is_corrected = Column(Boolean, default=False)
    corrected_value = Column(String(500), nullable=True)
    corrected_by = Column(String(100), nullable=True)
    corrected_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="extracted_fields")
