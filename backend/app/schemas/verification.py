from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.verification import VerificationStatus


class VerificationTriggerRequest(BaseModel):
    certificate_number: str
    authority_name: str
    document_id: Optional[str] = None


class VerificationResultResponse(BaseModel):
    id: int
    application_id: str
    document_id: Optional[str] = None
    authority_name: str
    certificate_number: str
    status: VerificationStatus
    is_simulated: bool = True
    check_timestamp: datetime
    mismatch_details: Optional[str] = None

    class Config:
        from_attributes = True


class MockAuthorityRecordResponse(BaseModel):
    id: int
    authority_name: str
    certificate_number: str
    institution_id: str
    institution_name: str
    doc_type: str
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    status: str
    is_simulated: bool = True

    class Config:
        from_attributes = True
