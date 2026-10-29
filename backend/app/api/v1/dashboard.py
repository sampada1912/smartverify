from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.user import User, UserRole
from app.models.application import Application, ApplicationStatus, ValidationOverallStatus
from app.models.validation import ValidationFinding, FindingCategory, FindingStatus
from app.models.verification import VerificationResult
from app.models.audit import AuditEvent
from app.schemas.dashboard import DashboardStatsResponse
from app.schemas.application import ApplicationResponse
from app.schemas.audit import AuditEventResponse
from app.services.auth_service import get_current_user
from app.api.v1.applications import _populate_app_counts

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.INSTITUTION:
        inst_id = current_user.institution_id
        apps_query = db.query(Application).filter(Application.institution_id == inst_id)
        total_apps = apps_query.count()
        draft_apps = apps_query.filter(Application.status == ApplicationStatus.DRAFT).count()
        submitted_apps = apps_query.filter(Application.status != ApplicationStatus.DRAFT).count()
        
        apps_needing_review = apps_query.filter(
            Application.validation_status.in_([
                ValidationOverallStatus.DEFICIENCIES_DETECTED,
                ValidationOverallStatus.HIGH_RISK
            ])
        ).count()

        inst_app_ids = [a.id for a in apps_query.all()]
        open_findings = db.query(ValidationFinding).filter(
            ValidationFinding.application_id.in_(inst_app_ids),
            ValidationFinding.status.in_([FindingStatus.OPEN, FindingStatus.UNDER_REVIEW])
        ).count()

        missing_docs = db.query(ValidationFinding).filter(
            ValidationFinding.application_id.in_(inst_app_ids),
            ValidationFinding.category == FindingCategory.MISSING_DOCUMENT,
            ValidationFinding.status.in_([FindingStatus.OPEN, FindingStatus.UNDER_REVIEW])
        ).count()

        expired_docs = db.query(ValidationFinding).filter(
            ValidationFinding.application_id.in_(inst_app_ids),
            ValidationFinding.category == FindingCategory.EXPIRED_DOCUMENT,
            ValidationFinding.status.in_([FindingStatus.OPEN, FindingStatus.UNDER_REVIEW])
        ).count()

        verifs = db.query(VerificationResult).filter(VerificationResult.application_id.in_(inst_app_ids)).all()
        verif_dist: Dict[str, int] = {}
        for v in verifs:
            key = v.status.value
            verif_dist[key] = verif_dist.get(key, 0) + 1

        apps = apps_query.all()
        cat_dist: Dict[str, int] = {}
        for a in apps:
            key = a.category.value
            cat_dist[key] = cat_dist.get(key, 0) + 1

        recent_audits = db.query(AuditEvent).filter(
            (AuditEvent.application_id.in_(inst_app_ids)) | (AuditEvent.actor_id == current_user.username)
        ).order_by(desc(AuditEvent.timestamp)).limit(8).all()
        
        recent_apps = apps_query.order_by(desc(Application.created_at)).limit(5).all()
        recent_app_responses = [_populate_app_counts(a, db) for a in recent_apps]
    else:
        total_apps = db.query(Application).count()
        draft_apps = db.query(Application).filter(Application.status == ApplicationStatus.DRAFT).count()
        submitted_apps = db.query(Application).filter(Application.status != ApplicationStatus.DRAFT).count()
        
        apps_needing_review = db.query(Application).filter(
            Application.validation_status.in_([
                ValidationOverallStatus.DEFICIENCIES_DETECTED,
                ValidationOverallStatus.HIGH_RISK
            ])
        ).count()

        open_findings = db.query(ValidationFinding).filter(
            ValidationFinding.status.in_([FindingStatus.OPEN, FindingStatus.UNDER_REVIEW])
        ).count()

        missing_docs = db.query(ValidationFinding).filter(
            ValidationFinding.category == FindingCategory.MISSING_DOCUMENT,
            ValidationFinding.status.in_([FindingStatus.OPEN, FindingStatus.UNDER_REVIEW])
        ).count()

        expired_docs = db.query(ValidationFinding).filter(
            ValidationFinding.category == FindingCategory.EXPIRED_DOCUMENT,
            ValidationFinding.status.in_([FindingStatus.OPEN, FindingStatus.UNDER_REVIEW])
        ).count()

        verifs = db.query(VerificationResult).all()
        verif_dist: Dict[str, int] = {}
        for v in verifs:
            key = v.status.value
            verif_dist[key] = verif_dist.get(key, 0) + 1

        apps = db.query(Application).all()
        cat_dist: Dict[str, int] = {}
        for a in apps:
            key = a.category.value
            cat_dist[key] = cat_dist.get(key, 0) + 1

        recent_audits = db.query(AuditEvent).order_by(desc(AuditEvent.timestamp)).limit(8).all()
        recent_apps = db.query(Application).order_by(desc(Application.created_at)).limit(5).all()
        recent_app_responses = [_populate_app_counts(a, db) for a in recent_apps]

    return DashboardStatsResponse(
        total_applications=total_apps,
        draft_applications=draft_apps,
        submitted_applications=submitted_apps,
        applications_needing_review=apps_needing_review,
        open_findings_count=open_findings,
        missing_documents_count=missing_docs,
        expired_documents_count=expired_docs,
        verification_status_distribution=verif_dist,
        category_distribution=cat_dist,
        recent_activity=recent_audits,
        recent_applications=recent_app_responses
    )
