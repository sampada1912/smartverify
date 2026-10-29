from pydantic import BaseModel
from typing import Dict, List, Any
from app.schemas.application import ApplicationResponse
from app.schemas.audit import AuditEventResponse


class DashboardStatsResponse(BaseModel):
    total_applications: int
    draft_applications: int
    submitted_applications: int
    applications_needing_review: int
    open_findings_count: int
    missing_documents_count: int
    expired_documents_count: int
    verification_status_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    recent_activity: List[AuditEventResponse]
    recent_applications: List[ApplicationResponse]
