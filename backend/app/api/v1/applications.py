import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from app.database import get_db
from app.models.user import User, UserRole
from app.models.application import (
    Application,
    ApplicationCategory,
    ApplicationStatus,
    ValidationOverallStatus
)
from app.models.checklist import ChecklistRule, ApplicationChecklistItem
from app.models.validation import ValidationFinding, FindingSeverity, FindingStatus
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationListResponse
)
from app.services.auth_service import get_current_user, require_role, verify_application_access
from app.services.validation_engine import validation_engine
from app.services.compliance_engine import compliance_engine
from app.services.audit_service import record_audit_event

router = APIRouter(prefix="/applications", tags=["Applications"])


def _populate_app_counts(app: Application, db: Session) -> ApplicationResponse:
    doc_count = len(app.documents)
    findings = db.query(ValidationFinding).filter(
        ValidationFinding.application_id == app.id
    ).all()
    open_findings = [f for f in findings if f.status in [FindingStatus.OPEN, FindingStatus.UNDER_REVIEW]]
    high_findings = [f for f in open_findings if f.severity == FindingSeverity.HIGH]

    resp = ApplicationResponse.from_orm(app)
    resp.document_count = doc_count
    resp.open_findings_count = len(open_findings)
    resp.high_findings_count = len(high_findings)
    return resp


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    req: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Enforce institution ownership on creation: institution users cannot create applications for another institution
    if current_user.role == UserRole.INSTITUTION:
        if not current_user.institution_id:
            raise HTTPException(status_code=400, detail="Institution account missing linked institution_id")
        institution_id = current_user.institution_id
    else:
        institution_id = req.institution_id

    # Generate unique application ID
    random_suffix = uuid.uuid4().hex[:6].upper()
    app_id = f"APP-2026-{random_suffix}"

    app = Application(
        id=app_id,
        institution_id=institution_id,
        institution_name=req.institution_name,
        category=req.category,
        academic_year=req.academic_year,
        programme=req.programme,
        course_name=req.course_name,
        existing_intake=req.existing_intake,
        requested_intake=req.requested_intake,
        contact_person=req.contact_person,
        contact_email=req.contact_email,
        contact_phone=req.contact_phone,
        status=ApplicationStatus.DRAFT,
        validation_status=ValidationOverallStatus.NOT_EVALUATED,
        created_at=datetime.utcnow()
    )
    db.add(app)
    db.commit()

    # Seed applicable checklist items from master ChecklistRules
    rules = db.query(ChecklistRule).filter(
        ChecklistRule.is_active == True,
        or_(ChecklistRule.category == "ALL", ChecklistRule.category == req.category.value)
    ).all()

    for r in rules:
        chk_item = ApplicationChecklistItem(
            application_id=app.id,
            rule_code=r.rule_code,
            requirement_name=r.requirement_name,
            document_type=r.document_type,
            is_required=r.is_required,
            is_submitted=False,
            validation_status="MISSING",
            explanation=f"Pending submission of {r.requirement_name}"
        )
        db.add(chk_item)

    db.commit()

    # Record Audit Event
    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role.value,
        action="APPLICATION_CREATED",
        entity_type="APPLICATION",
        entity_id=app.id,
        application_id=app.id,
        after_state=f"Created draft for {app.institution_name} ({app.category.value})"
    )

    db.refresh(app)
    return _populate_app_counts(app, db)


@router.get("", response_model=ApplicationListResponse)
def list_applications(
    category: Optional[ApplicationCategory] = None,
    app_status: Optional[ApplicationStatus] = Query(None, alias="status"),
    validation_status: Optional[ValidationOverallStatus] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Application)

    # Institution role scoping (if user is institution, show their institution's applications)
    if current_user.role == UserRole.INSTITUTION and current_user.institution_id:
        query = query.filter(Application.institution_id == current_user.institution_id)

    if category:
        query = query.filter(Application.category == category)
    if app_status:
        query = query.filter(Application.status == app_status)
    if validation_status:
        query = query.filter(Application.validation_status == validation_status)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Application.id.ilike(search_pattern),
                Application.institution_name.ilike(search_pattern),
                Application.institution_id.ilike(search_pattern),
                Application.course_name.ilike(search_pattern)
            )
        )

    total = query.count()
    apps = query.order_by(desc(Application.created_at)).offset(skip).limit(limit).all()
    items = [_populate_app_counts(a, db) for a in apps]

    return ApplicationListResponse(total=total, items=items)


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = verify_application_access(application_id, db, current_user)
    return _populate_app_counts(app, db)


@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: str,
    req: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = verify_application_access(application_id, db, current_user)

    before_state = f"Intake: {app.existing_intake}->{app.requested_intake}, Status: {app.status.value}"

    for field, val in req.dict(exclude_unset=True).items():
        setattr(app, field, val)

    app.updated_at = datetime.utcnow()
    db.commit()

    # Re-run validation if intake or course modified
    validation_engine.run_validation(db, app.id)
    compliance_engine.evaluate_compliance(db, app.id)

    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role.value,
        action="APPLICATION_UPDATED",
        entity_type="APPLICATION",
        entity_id=app.id,
        application_id=app.id,
        before_state=before_state,
        after_state=f"Updated application parameters"
    )

    db.refresh(app)
    return _populate_app_counts(app, db)


@router.post("/{application_id}/submit", response_model=ApplicationResponse)
def submit_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = verify_application_access(application_id, db, current_user)

    before_status = app.status.value
    app.status = ApplicationStatus.SUBMITTED
    app.submission_date = datetime.utcnow()
    db.commit()

    # Run automated scrutiny validation and compliance engines upon submission
    validation_engine.run_validation(db, app.id)
    compliance_engine.evaluate_compliance(db, app.id)

    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role.value,
        action="APPLICATION_SUBMITTED",
        entity_type="APPLICATION",
        entity_id=app.id,
        application_id=app.id,
        before_state=before_status,
        after_state=app.status.value,
        details="Application formally submitted by institution for regulatory scrutiny"
    )

    db.refresh(app)
    return _populate_app_counts(app, db)


@router.post("/{application_id}/reopen", response_model=ApplicationResponse)
def reopen_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = verify_application_access(application_id, db, current_user)

    app.status = ApplicationStatus.UNDER_SCRUTINY
    db.commit()

    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role.value,
        action="APPLICATION_REOPENED",
        entity_type="APPLICATION",
        entity_id=app.id,
        application_id=app.id,
        after_state="UNDER_SCRUTINY"
    )

    db.refresh(app)
    return _populate_app_counts(app, db)
