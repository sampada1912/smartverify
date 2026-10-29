import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.application import Application, ApplicationStatus
from app.models.validation import ValidationFinding, FindingStatus
from app.models.evidence_request import EvidenceRequest, EvidenceRequestStatus
from app.schemas.evidence_request import (
    EvidenceRequestCreate,
    EvidenceResponseSubmit,
    EvidenceRequestResponse
)
from app.services.auth_service import get_current_user, require_role, verify_application_access
from app.services.validation_engine import validation_engine
from app.services.compliance_engine import compliance_engine
from app.services.audit_service import record_audit_event

router = APIRouter(tags=["Evidence Requests"])


@router.post("/applications/{application_id}/evidence-requests", response_model=EvidenceRequestResponse)
def create_evidence_request(
    application_id: str,
    req: EvidenceRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.REVIEWER, UserRole.ADMIN]))
):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    req_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"
    ev_req = EvidenceRequest(
        id=req_id,
        application_id=app.id,
        finding_id=req.finding_id,
        requested_by=current_user.username,
        request_text=req.request_text,
        status=EvidenceRequestStatus.PENDING,
        requested_at=datetime.utcnow()
    )
    db.add(ev_req)

    # If linked to a finding, update finding status to REQUESTED_INFORMATION
    if req.finding_id:
        finding = db.query(ValidationFinding).filter(ValidationFinding.id == req.finding_id).first()
        if finding:
            finding.status = FindingStatus.REQUESTED_INFORMATION

    app.status = ApplicationStatus.DEFICIENCIES_COMMUNICATED
    db.commit()

    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role.value,
        action="EVIDENCE_REQUESTED",
        entity_type="EVIDENCE_REQUEST",
        entity_id=ev_req.id,
        application_id=app.id,
        after_state=f"Requested: {req.request_text[:60]}...",
        details=f"Deficiency inquiry communicated to institution for finding '{req.finding_id or 'General'}'"
    )

    db.refresh(ev_req)
    return ev_req


@router.get("/applications/{application_id}/evidence-requests", response_model=List[EvidenceRequestResponse])
def get_application_evidence_requests(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = verify_application_access(application_id, db, current_user)
    reqs = db.query(EvidenceRequest).filter(
        EvidenceRequest.application_id == app.id
    ).order_by(EvidenceRequest.requested_at.desc()).all()
    return reqs


@router.post("/evidence-requests/{request_id}/respond", response_model=EvidenceRequestResponse)
def respond_to_evidence_request(
    request_id: str,
    resp: EvidenceResponseSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ev_req = db.query(EvidenceRequest).filter(EvidenceRequest.id == request_id).first()
    if not ev_req:
        raise HTTPException(status_code=404, detail="Evidence request not found")

    # Enforce tenant isolation: user must have access to the application
    app = verify_application_access(ev_req.application_id, db, current_user)

    ev_req.status = EvidenceRequestStatus.RESPONDED
    ev_req.response_text = resp.response_text
    ev_req.response_document_id = resp.response_document_id
    ev_req.responded_at = datetime.utcnow()

    # Update finding back to UNDER_REVIEW
    if ev_req.finding_id:
        finding = db.query(ValidationFinding).filter(ValidationFinding.id == ev_req.finding_id).first()
        if finding:
            finding.status = FindingStatus.UNDER_REVIEW

    # Update application back to UNDER_SCRUTINY
    app = db.query(Application).filter(Application.id == ev_req.application_id).first()
    if app:
        app.status = ApplicationStatus.UNDER_SCRUTINY

    db.commit()

    # Re-run validation checks
    validation_engine.run_validation(db, ev_req.application_id)
    compliance_engine.evaluate_compliance(db, ev_req.application_id)

    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role.value,
        action="EVIDENCE_SUBMITTED",
        entity_type="EVIDENCE_REQUEST",
        entity_id=ev_req.id,
        application_id=ev_req.application_id,
        after_state="RESPONDED",
        details=f"Institution explanation: {resp.response_text[:80]}..."
    )

    db.refresh(ev_req)
    return ev_req
