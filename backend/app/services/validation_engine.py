import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.application import Application, ValidationOverallStatus
from app.models.document import Document, DocumentType
from app.models.extracted_field import ExtractedField
from app.models.checklist import ApplicationChecklistItem
from app.models.validation import (
    ValidationFinding,
    FindingCategory,
    FindingSeverity,
    FindingStatus
)
from app.models.synthetic_record import SyntheticInstitutionRecord


class ValidationEngine:
    def run_validation(self, db: Session, application_id: str) -> List[ValidationFinding]:
        app = db.query(Application).filter(Application.id == application_id).first()
        if not app:
            return []

        # Fetch existing findings to preserve resolutions and overrides
        existing_findings = {f.id: f for f in app.findings}
        existing_by_key = {
            f"{f.category.value}:{f.document_id}:{f.title}": f
            for f in app.findings
        }

        new_findings: List[ValidationFinding] = []
        docs = app.documents
        doc_map = {d.id: d for d in docs}
        
        # 1. Check Missing Required Documents
        self._check_missing_documents(db, app, existing_by_key, new_findings)

        # 2. Check Document Fields, Expiry, Identifiers
        self._check_document_level_rules(db, app, docs, existing_by_key, new_findings)

        # 3. Check Application vs Synthetic Institutional Record
        self._check_synthetic_record_mismatches(db, app, existing_by_key, new_findings)

        # 4. Check Intake and Category Logic
        self._check_intake_logic(db, app, docs, existing_by_key, new_findings)

        # 5. Check Duplicates and Anomalies
        self._check_duplicates_and_anomalies(db, app, docs, existing_by_key, new_findings)

        # Add newly generated findings to database
        for f in new_findings:
            db.add(f)
        db.commit()

        # Re-fetch all current findings for application
        all_current_findings = db.query(ValidationFinding).filter(
            ValidationFinding.application_id == application_id
        ).all()

        # Update application overall validation status
        open_findings = [f for f in all_current_findings if f.status in [FindingStatus.OPEN, FindingStatus.UNDER_REVIEW]]
        high_severity_open = [f for f in open_findings if f.severity == FindingSeverity.HIGH]

        if not open_findings:
            app.validation_status = ValidationOverallStatus.CLEAN
        elif len(high_severity_open) >= 3:
            app.validation_status = ValidationOverallStatus.HIGH_RISK
        else:
            app.validation_status = ValidationOverallStatus.DEFICIENCIES_DETECTED

        db.commit()
        return all_current_findings

    def _create_or_keep_finding(
        self,
        existing_by_key: Dict[str, ValidationFinding],
        new_findings: List[ValidationFinding],
        application_id: str,
        category: FindingCategory,
        severity: FindingSeverity,
        title: str,
        explanation: str,
        expected_value: Optional[str] = None,
        observed_value: Optional[str] = None,
        source_record: Optional[str] = None,
        document_id: Optional[str] = None,
        page_number: Optional[int] = None,
        evidence_snippet: Optional[str] = None,
        recommended_action: str = "Please verify document or submit fresh evidence."
    ):
        key = f"{category.value}:{document_id}:{title}"
        if key in existing_by_key:
            # Finding already exists, do not overwrite reviewer override or resolution
            return

        finding_id = f"FIND-{uuid.uuid4().hex[:8].upper()}"
        finding = ValidationFinding(
            id=finding_id,
            application_id=application_id,
            document_id=document_id,
            category=category,
            severity=severity,
            status=FindingStatus.OPEN,
            title=title,
            explanation=explanation,
            expected_value=expected_value,
            observed_value=observed_value,
            source_record=source_record,
            page_number=page_number,
            evidence_snippet=evidence_snippet,
            recommended_action=recommended_action,
            detection_timestamp=datetime.utcnow()
        )
        new_findings.append(finding)

    def _check_missing_documents(
        self,
        db: Session,
        app: Application,
        existing_by_key: Dict[str, ValidationFinding],
        new_findings: List[ValidationFinding]
    ):
        checklist_items = db.query(ApplicationChecklistItem).filter(
            ApplicationChecklistItem.application_id == app.id
        ).all()

        for item in checklist_items:
            if item.is_required and not item.is_submitted:
                self._create_or_keep_finding(
                    existing_by_key=existing_by_key,
                    new_findings=new_findings,
                    application_id=app.id,
                    category=FindingCategory.MISSING_DOCUMENT,
                    severity=FindingSeverity.HIGH,
                    title=f"Missing Mandatory Document: {item.requirement_name}",
                    explanation=f"Under application category '{app.category.value}', '{item.requirement_name}' is mandatory but has not been uploaded.",
                    expected_value=f"Uploaded {item.document_type} file",
                    observed_value="Not Submitted",
                    source_record=f"Checklist Rule {item.rule_code}",
                    recommended_action=f"Upload the signed and authenticated {item.requirement_name} document."
                )

    def _check_document_level_rules(
        self,
        db: Session,
        app: Application,
        docs: List[Document],
        existing_by_key: Dict[str, ValidationFinding],
        new_findings: List[ValidationFinding]
    ):
        today_str = datetime.utcnow().strftime("%Y-%m-%d")

        for doc in docs:
            fields = db.query(ExtractedField).filter(ExtractedField.document_id == doc.id).all()
            field_map = {f.field_name: f for f in fields}

            # 1. Institution ID Consistency check
            if "institution_id" in field_map:
                f_id = field_map["institution_id"]
                val = f_id.normalized_value or f_id.extracted_value
                if val and app.institution_id:
                    if val.strip() != app.institution_id.strip():
                        self._create_or_keep_finding(
                            existing_by_key=existing_by_key,
                            new_findings=new_findings,
                            application_id=app.id,
                            document_id=doc.id,
                            category=FindingCategory.ID_MISMATCH,
                            severity=FindingSeverity.HIGH,
                            title=f"Institution ID Mismatch in {doc.doc_type.value}",
                            explanation=f"Document specifies Institution ID '{val}', which does not match application ID '{app.institution_id}'.",
                            expected_value=app.institution_id,
                            observed_value=val,
                            source_record=f"Document: {doc.original_filename}",
                            page_number=f_id.page_number,
                            evidence_snippet=f_id.snippet,
                            recommended_action="Ensure document belongs to the applying institution and verify the permanent institute id."
                        )

            # 2. Document Expiry Check
            if "expiry_date" in field_map:
                f_exp = field_map["expiry_date"]
                exp_val = f_exp.normalized_value
                # If date format is YYYY-MM-DD
                if exp_val and len(exp_val) == 10 and exp_val < today_str:
                    self._create_or_keep_finding(
                        existing_by_key=existing_by_key,
                        new_findings=new_findings,
                        application_id=app.id,
                        document_id=doc.id,
                        category=FindingCategory.EXPIRED_DOCUMENT,
                        severity=FindingSeverity.HIGH,
                        title=f"Expired Document: {doc.doc_type.value}",
                        explanation=f"The uploaded document validity expired on {exp_val}. Current regulatory scrutiny requires active validity.",
                        expected_value=f"Validity >= {today_str}",
                        observed_value=f"Expired on {exp_val}",
                        source_record=f"Document: {doc.original_filename}",
                        page_number=f_exp.page_number,
                        evidence_snippet=f_exp.snippet,
                        recommended_action="Upload an updated, renewed certificate or an official extension endorsement."
                    )

            # 3. Previous Approval Letter Intake vs Claimed Existing Intake
            if doc.doc_type == DocumentType.PREVIOUS_APPROVAL and "approved_intake" in field_map:
                f_intake = field_map["approved_intake"]
                try:
                    doc_intake = int(f_intake.normalized_value)
                    if doc_intake != app.existing_intake:
                        self._create_or_keep_finding(
                            existing_by_key=existing_by_key,
                            new_findings=new_findings,
                            application_id=app.id,
                            document_id=doc.id,
                            category=FindingCategory.FIELD_MISMATCH,
                            severity=FindingSeverity.HIGH,
                            title="Previous Approved Intake Mismatch",
                            explanation=f"Previous approval letter specifies an intake of {doc_intake}, but application form declares existing approved intake as {app.existing_intake}.",
                            expected_value=str(doc_intake),
                            observed_value=str(app.existing_intake),
                            source_record=f"Document: {doc.original_filename}",
                            page_number=f_intake.page_number,
                            evidence_snippet=f_intake.snippet,
                            recommended_action="Reconcile the declared existing intake with the previous official approval letter."
                        )
                except ValueError:
                    pass

    def _check_synthetic_record_mismatches(
        self,
        db: Session,
        app: Application,
        existing_by_key: Dict[str, ValidationFinding],
        new_findings: List[ValidationFinding]
    ):
        syn_rec = db.query(SyntheticInstitutionRecord).filter(
            SyntheticInstitutionRecord.institution_id == app.institution_id
        ).first()

        if syn_rec:
            # Check baseline intake
            if syn_rec.approved_intake != app.existing_intake:
                self._create_or_keep_finding(
                    existing_by_key=existing_by_key,
                    new_findings=new_findings,
                    application_id=app.id,
                    category=FindingCategory.INSTITUTIONAL_RECORD_MISMATCH,
                    severity=FindingSeverity.HIGH,
                    title="Discrepancy with Institutional Master Registry Record",
                    explanation=f"According to synthetic institutional records, approved intake for {app.academic_year} was {syn_rec.approved_intake}, but application claims {app.existing_intake}.",
                    expected_value=f"{syn_rec.approved_intake} seats",
                    observed_value=f"{app.existing_intake} seats",
                    source_record=f"Institutional Master Registry (ID: {syn_rec.institution_id})",
                    recommended_action="Review past council orders or rectify application declared intake."
                )

    def _check_intake_logic(
        self,
        db: Session,
        app: Application,
        docs: List[Document],
        existing_by_key: Dict[str, ValidationFinding],
        new_findings: List[ValidationFinding]
    ):
        # If requested intake is greater than 2x existing intake, check if NBA accreditation is present
        if app.requested_intake > (app.existing_intake * 1.5):
            has_accreditation = any(d.doc_type == DocumentType.ACCREDITATION_CERT for d in docs)
            if not has_accreditation:
                self._create_or_keep_finding(
                    existing_by_key=existing_by_key,
                    new_findings=new_findings,
                    application_id=app.id,
                    category=FindingCategory.INTAKE_INCONSISTENCY,
                    severity=FindingSeverity.HIGH,
                    title="Substantial Intake Increase Lacks Mandatory Accreditation Evidence",
                    explanation=f"Requested intake increase from {app.existing_intake} to {app.requested_intake} (>50% increase) requires valid NBA accreditation certificate as per regulatory norms.",
                    expected_value="Valid NBA Accreditation Certificate submitted",
                    observed_value="No Accreditation Evidence found",
                    source_record="Approval Process Handbook Norms",
                    recommended_action="Submit current NBA accreditation proof or revise requested intake."
                )

    def _check_duplicates_and_anomalies(
        self,
        db: Session,
        app: Application,
        docs: List[Document],
        existing_by_key: Dict[str, ValidationFinding],
        new_findings: List[ValidationFinding]
    ):
        seen_hashes = {}
        for doc in docs:
            # Check within-application duplicate hash
            if doc.sha256_hash in seen_hashes:
                other_doc = seen_hashes[doc.sha256_hash]
                self._create_or_keep_finding(
                    existing_by_key=existing_by_key,
                    new_findings=new_findings,
                    application_id=app.id,
                    document_id=doc.id,
                    category=FindingCategory.DUPLICATE_DOCUMENT,
                    severity=FindingSeverity.HIGH,
                    title="Exact Duplicate Document Uploaded",
                    explanation=f"Document '{doc.original_filename}' has identical SHA-256 fingerprint ({doc.sha256_hash[:12]}...) to '{other_doc.original_filename}'.",
                    expected_value="Distinct, independent supporting documents",
                    observed_value=f"Identical hash to document ID {other_doc.id}",
                    source_record=f"Document: {doc.original_filename}",
                    recommended_action="Remove duplicate upload and attach the correct distinct requirement file."
                )
            else:
                seen_hashes[doc.sha256_hash] = doc

            # Check cross-application duplicate hash
            conflict_doc = db.query(Document).filter(
                Document.sha256_hash == doc.sha256_hash,
                Document.application_id != app.id
            ).first()

            if conflict_doc:
                self._create_or_keep_finding(
                    existing_by_key=existing_by_key,
                    new_findings=new_findings,
                    application_id=app.id,
                    document_id=doc.id,
                    category=FindingCategory.DUPLICATE_DOCUMENT,
                    severity=FindingSeverity.HIGH,
                    title="Cross-Application Duplicate Document Detected",
                    explanation=f"File content SHA-256 fingerprint is identical to document in application '{conflict_doc.application_id}'.",
                    expected_value="Institution-specific authentic document",
                    observed_value=f"Duplicate of {conflict_doc.application_id} / {conflict_doc.original_filename}",
                    source_record=f"Document: {doc.original_filename}",
                    recommended_action="Investigate why an identical binary document was submitted across different applications."
                )

            # Metadata anomaly check (review indicator only)
            if doc.pdf_metadata_json:
                try:
                    meta = json.loads(doc.pdf_metadata_json)
                    mod_date = meta.get("modDate", "")
                    create_date = meta.get("creationDate", "")
                    # If modDate is present and creationDate is empty or distinctly unusual
                    if mod_date and "D:" in mod_date and "2026" in mod_date:
                        fields = db.query(ExtractedField).filter(ExtractedField.document_id == doc.id).all()
                        issue_f = next((f for f in fields if f.field_name == "issue_date"), None)
                        if issue_f and issue_f.normalized_value and issue_f.normalized_value < "2024-01-01":
                            self._create_or_keep_finding(
                                existing_by_key=existing_by_key,
                                new_findings=new_findings,
                                application_id=app.id,
                                document_id=doc.id,
                                category=FindingCategory.ANOMALY,
                                severity=FindingSeverity.INFO,
                                title="Metadata Modification Timestamp Indicator",
                                explanation=f"Document stated issue date is {issue_f.normalized_value}, but PDF metadata shows modification in {mod_date[:6]}. Note: This is a review indicator only, not proof of tampering.",
                                expected_value=f"Consistent timestamp with issue date",
                                observed_value=f"PDF Metadata modDate: {mod_date}",
                                source_record=f"Document Metadata: {doc.original_filename}",
                                page_number=1,
                                recommended_action="Manual visual inspection of seals and signatures recommended."
                            )
                except Exception:
                    pass


validation_engine = ValidationEngine()
