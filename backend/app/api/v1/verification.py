import json
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.application import Application
from app.models.verification import MockAuthorityRecord, VerificationResult, VerificationStatus
from app.schemas.verification import (
    VerificationTriggerRequest,
    VerificationResultResponse,
    MockAuthorityRecordResponse
)
from app.services.auth_service import get_current_user, verify_application_access
from app.services.verification_adapter import verification_adapter
from app.services.compliance_engine import compliance_engine
from app.services.audit_service import record_audit_event

router = APIRouter(tags=["Verification Adapter"])


@router.post("/applications/{application_id}/verify", response_model=VerificationResultResponse)
def trigger_verification(
    application_id: str,
    req: VerificationTriggerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = verify_application_access(application_id, db, current_user)

    submitted_data = {
        "institution_id": app.institution_id,
        "institution_name": app.institution_name,
        "programme": app.programme,
        "course_name": app.course_name
    }

    outcome = verification_adapter.verify(
        db=db,
        authority_name=req.authority_name,
        certificate_number=req.certificate_number,
        submitted_data=submitted_data
    )

    verif_res = VerificationResult(
        application_id=app.id,
        document_id=req.document_id,
        authority_name=outcome.authority_name,
        certificate_number=outcome.certificate_number,
        status=outcome.status,
        is_simulated=outcome.is_simulated,
        check_timestamp=datetime.utcnow(),
        mismatch_details=outcome.mismatch_details,
        raw_response_json=json.dumps(outcome.raw_response)
    )
    db.add(verif_res)
    db.commit()

    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role.value,
        action="AUTHORITY_VERIFICATION_CHECK",
        entity_type="VERIFICATION_RESULT",
        entity_id=str(verif_res.id),
        application_id=app.id,
        after_state=f"{outcome.authority_name}: {outcome.status.value}",
        details=f"Certificate: {outcome.certificate_number}; Simulated: True; Details: {outcome.mismatch_details or 'OK'}"
    )

    # Re-evaluate compliance since verification outcome may impact rules
    compliance_engine.evaluate_compliance(db, app.id)

    db.refresh(verif_res)
    return verif_res


@router.get("/applications/{application_id}/verification", response_model=List[VerificationResultResponse])
def get_application_verification_results(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_application_access(application_id, db, current_user)
    results = db.query(VerificationResult).filter(
        VerificationResult.application_id == application_id
    ).order_by(VerificationResult.check_timestamp.desc()).all()
    return results


@router.get("/verification/mock-records", response_model=List[MockAuthorityRecordResponse])
def list_mock_authority_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns simulated records in the mock issuing authority registry for demonstration."""
    records = db.query(MockAuthorityRecord).all()
    return records
