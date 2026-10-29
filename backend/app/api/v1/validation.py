from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.validation import ValidationFinding, FindingStatus
from app.schemas.validation import (
    FindingResponse,
    FindingResolutionRequest,
    FindingOverrideRequest
)
from app.services.auth_service import get_current_user, require_role, verify_application_access
from app.services.validation_engine import validation_engine
from app.services.audit_service import record_audit_event

router = APIRouter(tags=["Validation & Findings"])


@router.post("/applications/{application_id}/validate", response_model=List[FindingResponse])
def trigger_application_validation(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = verify_application_access(application_id, db, current_user)
    findings = validation_engine.run_validation(db, app.id)
    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role.value,
        action="VALIDATION_RUN",
        entity_type="APPLICATION",
        entity_id=application_id,
        application_id=application_id,
        details=f"Evaluated deterministic validation rules; produced {len(findings)} finding(s)"
    )
    return findings


@router.get("/applications/{application_id}/findings", response_model=List[FindingResponse])
def get_application_findings(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = verify_application_access(application_id, db, current_user)
    findings = db.query(ValidationFinding).filter(
        ValidationFinding.application_id == app.id
    ).order_by(ValidationFinding.detection_timestamp.desc()).all()
    return findings


@router.put("/findings/{finding_id}/resolve", response_model=FindingResponse)
def resolve_finding(
    finding_id: str,
    req: FindingResolutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.REVIEWER, UserRole.ADMIN]))
):
    finding = db.query(ValidationFinding).filter(ValidationFinding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    before_status = finding.status.value
    if req.action == "RESOLVE":
        finding.status = FindingStatus.RESOLVED
    elif req.action == "ESCALATE":
        finding.status = FindingStatus.ESCALATED
    elif req.action == "UNDER_REVIEW":
        finding.status = FindingStatus.UNDER_REVIEW

    finding.resolution_notes = req.resolution_notes
    finding.resolved_by = current_user.username
    finding.resolved_at = datetime.utcnow()
    db.commit()

    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role.value,
        action=f"FINDING_{finding.status.value}",
        entity_type="FINDING",
        entity_id=finding.id,
        application_id=finding.application_id,
        before_state=before_status,
        after_state=finding.status.value,
        details=f"Reviewer resolution: {req.resolution_notes}"
    )

    # Recompute overall application status
    validation_engine.run_validation(db, finding.application_id)

    db.refresh(finding)
    return finding


@router.put("/findings/{finding_id}/override", response_model=FindingResponse)
def override_finding_status(
    finding_id: str,
    req: FindingOverrideRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.REVIEWER, UserRole.ADMIN]))
):
    if not req.override_reason or len(req.override_reason.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A mandatory detailed override justification is required.",
        )

    finding = db.query(ValidationFinding).filter(ValidationFinding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    before_status = finding.status.value
    finding.status = req.new_status
    finding.override_reason = req.override_reason
    finding.resolved_by = current_user.username
    finding.resolved_at = datetime.utcnow()
    db.commit()

    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role.value,
        action="FINDING_OVERRIDDEN",
        entity_type="FINDING",
        entity_id=finding.id,
        application_id=finding.application_id,
        before_state=before_status,
        after_state=finding.status.value,
        details=f"Mandatory Override Reason: {req.override_reason}"
    )

    # Recompute overall application status
    validation_engine.run_validation(db, finding.application_id)

    db.refresh(finding)
    return finding
