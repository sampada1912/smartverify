from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.extracted_field import ExtractedField
from app.schemas.extracted_field import ExtractedFieldResponse, ExtractedFieldCorrectionRequest
from app.services.auth_service import get_current_user, require_role, verify_application_access, verify_document_access
from app.services.validation_engine import validation_engine
from app.services.compliance_engine import compliance_engine
from app.services.audit_service import record_audit_event

router = APIRouter(tags=["Extracted Fields"])


@router.get("/documents/{document_id}/fields", response_model=List[ExtractedFieldResponse])
def get_document_fields(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = verify_document_access(document_id, db, current_user)
    fields = db.query(ExtractedField).filter(ExtractedField.document_id == doc.id).all()
    return fields


@router.get("/applications/{application_id}/fields", response_model=List[ExtractedFieldResponse])
def get_application_all_fields(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = verify_application_access(application_id, db, current_user)
    fields = db.query(ExtractedField).filter(ExtractedField.application_id == app.id).all()
    return fields


@router.put("/fields/{field_id}/correct", response_model=ExtractedFieldResponse)
def correct_extracted_field(
    field_id: int,
    req: ExtractedFieldCorrectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.REVIEWER, UserRole.ADMIN]))
):
    field = db.query(ExtractedField).filter(ExtractedField.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Extracted field not found")

    before_val = field.normalized_value or field.extracted_value
    field.is_corrected = True
    field.corrected_value = req.corrected_value.strip()
    field.normalized_value = req.corrected_value.strip()
    field.corrected_by = current_user.username
    field.corrected_at = datetime.utcnow()
    db.commit()

    # Log audit event with mandatory justification
    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role.value,
        action="FIELD_CORRECTED",
        entity_type="EXTRACTED_FIELD",
        entity_id=str(field.id),
        application_id=field.application_id,
        before_state=f"{field.field_name}: '{before_val}'",
        after_state=f"{field.field_name}: '{field.corrected_value}'",
        details=f"Reviewer override justification: {req.justification}"
    )

    # Re-run validation and compliance since field value has been corrected
    validation_engine.run_validation(db, field.application_id)
    compliance_engine.evaluate_compliance(db, field.application_id)

    db.refresh(field)
    return field
