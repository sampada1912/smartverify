from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.evidence_request import EvidenceRequestStatus


class EvidenceRequestCreate(BaseModel):
    finding_id: Optional[str] = None
    request_text: str


class EvidenceResponseSubmit(BaseModel):
    response_text: str
    response_document_id: Optional[str] = None


class EvidenceRequestResponse(BaseModel):
    id: str
    application_id: str
    finding_id: Optional[str] = None
    requested_by: str
    request_text: str
    status: EvidenceRequestStatus
    response_text: Optional[str] = None
    response_document_id: Optional[str] = None
    requested_at: datetime
    responded_at: Optional[datetime] = None

    class Config:
        from_attributes = True
