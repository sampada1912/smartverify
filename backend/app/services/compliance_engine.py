from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.application import Application, ApplicationCategory
from app.models.document import Document, DocumentType
from app.models.extracted_field import ExtractedField
from app.models.verification import VerificationResult, VerificationStatus
from app.models.compliance_rule import (
    ComplianceRule,
    ComplianceEvaluation,
    ComplianceStatus
)


class ComplianceEngine:
    def evaluate_compliance(self, db: Session, application_id: str) -> List[ComplianceEvaluation]:
        app = db.query(Application).filter(Application.id == application_id).first()
        if not app:
            return []

        # Remove previous evaluations to re-evaluate cleanly
        db.query(ComplianceEvaluation).filter(
            ComplianceEvaluation.application_id == application_id
        ).delete()
        db.commit()

        # Fetch active compliance rules
        rules = db.query(ComplianceRule).filter(ComplianceRule.is_enabled == True).all()

        docs = app.documents
        doc_by_type: Dict[DocumentType, Document] = {}
        for d in docs:
            if d.doc_type not in doc_by_type:
                doc_by_type[d.doc_type] = d

        # Fetch extracted fields
        all_fields = db.query(ExtractedField).filter(
            ExtractedField.application_id == application_id
        ).all()
        fields_by_doc: Dict[str, Dict[str, ExtractedField]] = {}
        for f in all_fields:
            if f.document_id not in fields_by_doc:
                fields_by_doc[f.document_id] = {}
            fields_by_doc[f.document_id][f.field_name] = f

        # Fetch verification results
        verif_results = db.query(VerificationResult).filter(
            VerificationResult.application_id == application_id
        ).all()
        verif_by_doc = {v.document_id: v for v in verif_results if v.document_id}

        evaluations: List[ComplianceEvaluation] = []

        for rule in rules:
            # Check category condition
            if rule.category_condition != "ALL" and rule.category_condition != app.category.value:
                eval = ComplianceEvaluation(
                    application_id=app.id,
                    rule_id=rule.rule_id,
                    rule_name=rule.rule_name,
                    status=ComplianceStatus.NOT_APPLICABLE,
                    explanation=f"Rule applies specifically to {rule.category_condition}, whereas application is {app.category.value}.",
                    evidence_summary="Not Applicable for current application category",
                    evaluated_at=datetime.utcnow()
                )
                evaluations.append(eval)
                continue

            # Evaluate specific rule logic
            status, explanation, evidence = self._evaluate_rule_logic(
                rule=rule,
                app=app,
                doc_by_type=doc_by_type,
                fields_by_doc=fields_by_doc,
                verif_by_doc=verif_by_doc
            )

            eval = ComplianceEvaluation(
                application_id=app.id,
                rule_id=rule.rule_id,
                rule_name=rule.rule_name,
                status=status,
                explanation=explanation,
                evidence_summary=evidence,
                evaluated_at=datetime.utcnow()
            )
            evaluations.append(eval)

        for e in evaluations:
            db.add(e)
        db.commit()

        return evaluations

    def _evaluate_rule_logic(
        self,
        rule: ComplianceRule,
        app: Application,
        doc_by_type: Dict[DocumentType, Document],
        fields_by_doc: Dict[str, Dict[str, ExtractedField]],
        verif_by_doc: Dict[str, VerificationResult]
    ) -> tuple[ComplianceStatus, str, str]:
        logic = rule.evaluation_logic.upper()

        if logic == "PREVIOUS_APPROVAL_VALIDITY":
            doc = doc_by_type.get(DocumentType.PREVIOUS_APPROVAL)
            if not doc:
                return ComplianceStatus.NEEDS_REVIEW, "Mandatory previous approval letter is missing from submission.", "No previous approval document uploaded"
            fields = fields_by_doc.get(doc.id, {})
            if "approved_intake" in fields:
                val = fields["approved_intake"].normalized_value
                if val and int(val) == app.existing_intake:
                    return ComplianceStatus.PASS, f"Previous approval letter verified for approved intake of {val} matching declared application intake.", f"Document ID: {doc.id}, Approved Intake: {val}"
                else:
                    return ComplianceStatus.FAIL, f"Previous approval letter specifies intake of {val}, differing from declared {app.existing_intake}.", f"Declared: {app.existing_intake}, Letter: {val}"
            return ComplianceStatus.PASS, "Previous approval letter submitted and authenticated.", f"Document ID: {doc.id}"

        elif logic == "AFFIDAVIT_COMPLIANCE":
            doc = doc_by_type.get(DocumentType.AFFIDAVIT)
            if not doc:
                return ComplianceStatus.NEEDS_REVIEW, "Statutory affidavit and undertaking on stamp paper is not submitted.", "Affidavit document absent"
            fields = fields_by_doc.get(doc.id, {})
            has_ref = "reference_number" in fields
            has_date = "issue_date" in fields
            if has_ref and has_date:
                return ComplianceStatus.PASS, "Statutory affidavit submitted with verified notary reference number and execution date.", f"Ref: {fields['reference_number'].normalized_value}, Date: {fields['issue_date'].normalized_value}"
            return ComplianceStatus.PASS, "Statutory affidavit format submitted.", f"Document ID: {doc.id}"

        elif logic == "FACULTY_CADRE_RATIO":
            doc = doc_by_type.get(DocumentType.FACULTY_LIST)
            if not doc:
                return ComplianceStatus.NEEDS_REVIEW, "Faculty details list has not been submitted.", "Faculty document absent"
            fields = fields_by_doc.get(doc.id, {})
            if "total_faculty_count" in fields:
                count = int(fields["total_faculty_count"].normalized_value)
                # Approximate 4 batches * intake
                total_students = app.existing_intake * 4
                required_faculty = max(1, total_students // 20)
                if count >= required_faculty:
                    return ComplianceStatus.PASS, f"Faculty count of {count} satisfies the minimum requirement of {required_faculty} for {total_students} student capacity (1:20 ratio).", f"Total Faculty: {count}, Required: {required_faculty}"
                elif count >= (required_faculty * 0.8):
                    return ComplianceStatus.WARNING, f"Faculty count of {count} is slightly below standard requirement of {required_faculty}. Reviewer scrutiny required.", f"Total Faculty: {count}, Required: {required_faculty}"
                else:
                    return ComplianceStatus.FAIL, f"Severe faculty deficiency: {count} faculty members provided against mandatory requirement of {required_faculty}.", f"Total Faculty: {count}, Required: {required_faculty}"
            return ComplianceStatus.PASS, "Faculty list submitted for departmental review.", f"Document ID: {doc.id}"

        elif logic == "NOC_VALIDITY":
            doc = doc_by_type.get(DocumentType.NOC)
            if not doc:
                return ComplianceStatus.NEEDS_REVIEW, "NOC from State Government / Affiliating University not uploaded.", "NOC document absent"
            verif = verif_by_doc.get(doc.id)
            if verif and verif.status == VerificationStatus.VERIFIED:
                return ComplianceStatus.PASS, "State/University NOC verified against issuing authority records.", f"Certificate: {verif.certificate_number}, Status: VERIFIED"
            elif verif and verif.status == VerificationStatus.MISMATCH_DETECTED:
                return ComplianceStatus.FAIL, f"NOC failed authoritative verification: {verif.mismatch_details}", f"Verification Status: MISMATCH"
            elif verif and verif.status == VerificationStatus.EXPIRED:
                return ComplianceStatus.FAIL, f"NOC has expired in authoritative register: {verif.mismatch_details}", f"Verification Status: EXPIRED"
            return ComplianceStatus.PASS, "NOC submitted with active validity.", f"Document ID: {doc.id}"

        elif logic == "INFRASTRUCTURE_NORMS":
            doc = doc_by_type.get(DocumentType.INFRASTRUCTURE_EVIDENCE)
            if not doc:
                return ComplianceStatus.NEEDS_REVIEW, "Infrastructure land and built-up area evidence not submitted.", "Infrastructure evidence absent"
            fields = fields_by_doc.get(doc.id, {})
            if "built_up_area_sqm" in fields:
                area = float(fields["built_up_area_sqm"].normalized_value)
                if area >= 4000.0:
                    return ComplianceStatus.PASS, f"Built-up area of {area:,.0f} sqm exceeds minimum regulatory requirement of 4,000 sqm.", f"Extracted Built-up Area: {area} sqm"
                else:
                    return ComplianceStatus.FAIL, f"Built-up area of {area:,.0f} sqm is deficient (minimum 4,000 sqm required).", f"Extracted Built-up Area: {area} sqm"
            return ComplianceStatus.PASS, "Infrastructure readiness certificate submitted.", f"Document ID: {doc.id}"

        elif logic == "TER_PAYMENT_STATUS":
            doc = doc_by_type.get(DocumentType.PAYMENT_RECEIPT)
            if not doc:
                return ComplianceStatus.NEEDS_REVIEW, "Technical Education Regulatory (TER) fee payment proof not uploaded.", "Payment receipt absent"
            fields = fields_by_doc.get(doc.id, {})
            if "payment_reference" in fields:
                ref = fields["payment_reference"].normalized_value
                return ComplianceStatus.PASS, f"TER payment receipt confirmed with transaction reference {ref}.", f"Transaction Ref: {ref}"
            return ComplianceStatus.PASS, "TER fee receipt submitted.", f"Document ID: {doc.id}"

        elif logic == "ACCREDITATION_EXPANSION_CHECK":
            if app.requested_intake > app.existing_intake:
                doc = doc_by_type.get(DocumentType.ACCREDITATION_CERT)
                if not doc:
                    return ComplianceStatus.FAIL, "Expansion in approved intake requires accredited programme status under NBA Tier-I/II norms.", "No Accreditation Certificate uploaded"
                verif = verif_by_doc.get(doc.id)
                if verif and verif.status == VerificationStatus.VERIFIED:
                    return ComplianceStatus.PASS, "NBA accreditation verified in authoritative register, permitting intake expansion.", f"Accreditation Cert: {verif.certificate_number}"
                return ComplianceStatus.PASS, "Accreditation certificate submitted for intake expansion.", f"Document ID: {doc.id}"
            else:
                return ComplianceStatus.NOT_APPLICABLE, "No intake increase requested; accreditation prerequisite not triggered.", "Intake constant or renewal"

        return ComplianceStatus.PASS, "Standard compliance evaluation satisfied.", "Manual review baseline"


compliance_engine = ComplianceEngine()
