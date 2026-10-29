import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from app.database import Base


class DocumentType(str, enum.Enum):
    PREVIOUS_APPROVAL = "PREVIOUS_APPROVAL"
    AFFIDAVIT = "AFFIDAVIT"
    FACULTY_LIST = "FACULTY_LIST"
    NOC = "NOC"
    ACCREDITATION_CERT = "ACCREDITATION_CERT"
    INFRASTRUCTURE_EVIDENCE = "INFRASTRUCTURE_EVIDENCE"
    PAYMENT_RECEIPT = "PAYMENT_RECEIPT"
    OTHER = "OTHER"


class OCRStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(50), primary_key=True, index=True)
    application_id = Column(String(50), ForeignKey("applications.id"), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    sha256_hash = Column(String(64), index=True, nullable=False)
    
    doc_type = Column(Enum(DocumentType), default=DocumentType.OTHER, nullable=False)
    classification_confidence = Column(Float, default=0.0)
    classification_method = Column(String(100), default="KEYWORD_HEURISTIC")
    
    ocr_status = Column(Enum(OCRStatus), default=OCRStatus.PENDING, nullable=False)
    ocr_engine_used = Column(String(100), default="PYMUPDF_NATIVE")
    extracted_text = Column(Text, nullable=True)
    page_count = Column(Integer, default=1)
    pdf_metadata_json = Column(Text, nullable=True)
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    application = relationship("Application", back_populates="documents")
    extracted_fields = relationship("ExtractedField", back_populates="document", cascade="all, delete-orphan")
    findings = relationship("ValidationFinding", back_populates="document")
