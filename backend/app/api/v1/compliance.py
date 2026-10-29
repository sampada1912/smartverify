from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.checklist import ChecklistRule, ApplicationChecklistItem
from app.models.compliance_rule import ComplianceRule, ComplianceEvaluation
from app.schemas.checklist import (
    ChecklistRuleResponse,
    ChecklistRuleCreate,
    ChecklistRuleUpdate,
    ApplicationChecklistItemResponse
)
from app.schemas.compliance import (
    ComplianceRuleResponse,
    ComplianceRuleCreate,
    ComplianceRuleUpdate,
    ComplianceEvaluationResponse
)
from app.services.auth_service import get_current_user, require_role, verify_application_access
from app.services.compliance_engine import compliance_engine
from app.services.audit_service import record_audit_event

router = APIRouter(tags=["Compliance & Checklist Rules"])


@router.post("/applications/{application_id}/evaluate", response_model=List[ComplianceEvaluationResponse])
def evaluate_application_compliance(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = verify_application_access(application_id, db, current_user)
    evals = compliance_engine.evaluate_compliance(db, app.id)
    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role.value,
        action="COMPLIANCE_EVALUATED",
        entity_type="APPLICATION",
        entity_id=app.id,
        application_id=app.id,
        details=f"Evaluated regulatory compliance rules; completed {len(evals)} rule evaluations"
    )
    return evals


@router.get("/applications/{application_id}/compliance", response_model=List[ComplianceEvaluationResponse])
def get_application_compliance(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = verify_application_access(application_id, db, current_user)
    evals = db.query(ComplianceEvaluation).filter(
        ComplianceEvaluation.application_id == app.id
    ).all()
    if not evals:
        # Run if not evaluated yet
        evals = compliance_engine.evaluate_compliance(db, app.id)
    return evals


@router.get("/applications/{application_id}/checklist", response_model=List[ApplicationChecklistItemResponse])
def get_application_checklist(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = verify_application_access(application_id, db, current_user)
    items = db.query(ApplicationChecklistItem).filter(
        ApplicationChecklistItem.application_id == app.id
    ).all()
    return items


# --- Admin Rule Management ---

@router.get("/compliance/rules", response_model=List[ComplianceRuleResponse])
def list_compliance_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rules = db.query(ComplianceRule).all()
    return rules


@router.put("/compliance/rules/{rule_id}", response_model=ComplianceRuleResponse)
def update_compliance_rule(
    rule_id: str,
    req: ComplianceRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    rule = db.query(ComplianceRule).filter(ComplianceRule.rule_id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Compliance rule not found")

    before_state = f"Enabled: {rule.is_enabled}, Name: {rule.rule_name}"
    for k, v in req.dict(exclude_unset=True).items():
        setattr(rule, k, v)
    rule.updated_at = datetime.utcnow()
    db.commit()

    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role.value,
        action="RULE_CONFIG_CHANGED",
        entity_type="COMPLIANCE_RULE",
        entity_id=rule.rule_id,
        before_state=before_state,
        after_state=f"Enabled: {rule.is_enabled}, Name: {rule.rule_name}"
    )

    db.refresh(rule)
    return rule


@router.get("/checklist/rules", response_model=List[ChecklistRuleResponse])
def list_checklist_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rules = db.query(ChecklistRule).all()
    return rules


@router.put("/checklist/rules/{rule_code}", response_model=ChecklistRuleResponse)
def update_checklist_rule(
    rule_code: str,
    req: ChecklistRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    rule = db.query(ChecklistRule).filter(ChecklistRule.rule_code == rule_code).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Checklist rule not found")

    before_state = f"Active: {rule.is_active}, Required: {rule.is_required}"
    for k, v in req.dict(exclude_unset=True).items():
        setattr(rule, k, v)
    rule.updated_at = datetime.utcnow()
    db.commit()

    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role.value,
        action="CHECKLIST_CONFIG_CHANGED",
        entity_type="CHECKLIST_RULE",
        entity_id=rule.rule_code,
        before_state=before_state,
        after_state=f"Active: {rule.is_active}, Required: {rule.is_required}"
    )

    db.refresh(rule)
    return rule
