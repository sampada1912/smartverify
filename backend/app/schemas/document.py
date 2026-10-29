from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.document import DocumentType, OCRStatus


class DocumentResponse(BaseModel):
    id: str
    application_id: str
    original_filename: str
    stored_filename: str
    file_size_bytes: int
    mime_type: str
    sha256_hash: str
    doc_type: DocumentType
    classification_confidence: float
    classification_method: str
    ocr_status: OCRStatus
    ocr_engine_used: str
    page_count: int
    uploaded_at: datetime
    extracted_text_preview: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    message: str
    documents: List[DocumentResponse]
