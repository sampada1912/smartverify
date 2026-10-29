from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.compliance_rule import ComplianceStatus, ComplianceRuleSeverity


class ComplianceRuleBase(BaseModel):
    rule_id: str
    rule_name: str
    description: str
    category_condition: str = "ALL"
    required_evidence_type: str
    evaluation_logic: str
    severity: ComplianceRuleSeverity = ComplianceRuleSeverity.HIGH
    is_enabled: bool = True
    version: str = "2026.1-ILLUSTRATIVE"
    effective_date: str = "2026-01-01"


class ComplianceRuleCreate(ComplianceRuleBase):
    pass


class ComplianceRuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    severity: Optional[ComplianceRuleSeverity] = None


class ComplianceRuleResponse(ComplianceRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComplianceEvaluationResponse(BaseModel):
    id: int
    application_id: str
    rule_id: str
    rule_name: str
    status: ComplianceStatus
    explanation: str
    evidence_summary: Optional[str] = None
    evaluated_at: datetime

    class Config:
        from_attributes = True
