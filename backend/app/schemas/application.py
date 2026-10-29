from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.application import ApplicationCategory, ApplicationStatus, ValidationOverallStatus


class ApplicationBase(BaseModel):
    institution_id: str
    institution_name: str
    category: ApplicationCategory = ApplicationCategory.EXTENSION_OF_APPROVAL
    academic_year: str = "2026-27"
    programme: str = "ENGINEERING_AND_TECHNOLOGY"
    course_name: str = "Computer Science and Engineering"
    existing_intake: int = 120
    requested_intake: int = 180
    contact_person: str
    contact_email: str
    contact_phone: str


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    institution_name: Optional[str] = None
    category: Optional[ApplicationCategory] = None
    academic_year: Optional[str] = None
    programme: Optional[str] = None
    course_name: Optional[str] = None
    existing_intake: Optional[int] = None
    requested_intake: Optional[int] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    id: str
    status: ApplicationStatus
    validation_status: ValidationOverallStatus
    assigned_reviewer_id: Optional[int] = None
    submission_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Counts
    document_count: Optional[int] = 0
    open_findings_count: Optional[int] = 0
    high_findings_count: Optional[int] = 0

    class Config:
        from_attributes = True


class ApplicationListResponse(BaseModel):
    total: int
    items: List[ApplicationResponse]
