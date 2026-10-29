from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.validation import FindingCategory, FindingSeverity, FindingStatus


class FindingResponse(BaseModel):
    id: str
    application_id: str
    document_id: Optional[str] = None
    category: FindingCategory
    severity: FindingSeverity
    status: FindingStatus
    title: str
    explanation: str
    expected_value: Optional[str] = None
    observed_value: Optional[str] = None
    source_record: Optional[str] = None
    page_number: Optional[int] = None
    evidence_snippet: Optional[str] = None
    recommended_action: str
    resolution_notes: Optional[str] = None
    override_reason: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    detection_timestamp: datetime

    class Config:
        from_attributes = True


class FindingResolutionRequest(BaseModel):
    resolution_notes: str
    action: str = "RESOLVE" # RESOLVE, ESCALATE, UNDER_REVIEW


class FindingOverrideRequest(BaseModel):
    new_status: FindingStatus
    override_reason: str # Mandatory explanation
