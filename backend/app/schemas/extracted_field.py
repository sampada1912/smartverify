from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ExtractedFieldResponse(BaseModel):
    id: int
    document_id: str
    application_id: str
    field_name: str
    extracted_value: str
    normalized_value: str
    page_number: int
    confidence: float
    extraction_method: str
    snippet: Optional[str] = None
    is_corrected: bool
    corrected_value: Optional[str] = None
    corrected_by: Optional[str] = None
    corrected_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ExtractedFieldCorrectionRequest(BaseModel):
    corrected_value: str
    justification: str
