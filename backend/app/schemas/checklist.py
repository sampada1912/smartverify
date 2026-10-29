from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChecklistRuleBase(BaseModel):
    rule_code: str
    category: str = "ALL"
    document_type: str
    requirement_name: str
    description: str
    is_required: bool = True
    is_active: bool = True
    version: str = "2026.1-PROTOTYPE"


class ChecklistRuleCreate(ChecklistRuleBase):
    pass


class ChecklistRuleUpdate(BaseModel):
    requirement_name: Optional[str] = None
    description: Optional[str] = None
    is_required: Optional[bool] = None
    is_active: Optional[bool] = None


class ChecklistRuleResponse(ChecklistRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationChecklistItemResponse(BaseModel):
    id: int
    application_id: str
    rule_code: str
    requirement_name: str
    document_type: str
    is_required: bool
    is_submitted: bool
    document_id: Optional[str] = None
    validation_status: str
    explanation: Optional[str] = None
    evidence_summary: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True
