import os
import sys
import shutil
import hashlib
import uuid
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import Base, engine, SessionLocal
from app.config import settings
from app.models.user import User, UserRole
from app.models.application import (
    Application,
    ApplicationCategory,
    ApplicationStatus,
    ValidationOverallStatus
)
from app.models.document import Document, DocumentType, OCRStatus
from app.models.extracted_field import ExtractedField
from app.models.checklist import ChecklistRule, ApplicationChecklistItem
from app.models.validation import (
    ValidationFinding,
    FindingCategory,
    FindingSeverity,
    FindingStatus
)
from app.models.verification import MockAuthorityRecord, VerificationResult, VerificationStatus
from app.models.compliance_rule import (
    ComplianceRule,
    ComplianceEvaluation,
    ComplianceStatus,
    ComplianceRuleSeverity
)
from app.models.synthetic_record import SyntheticInstitutionRecord
from app.models.evidence_request import EvidenceRequest, EvidenceRequestStatus
from app.models.audit import AuditEvent
from app.services.auth_service import get_password_hash
from app.services.ocr_service import ocr_service
from app.services.classifier_service import classifier_service
from app.services.extraction_service import extraction_service
from app.services.validation_engine import validation_engine
from app.services.compliance_engine import compliance_engine
from app.services.audit_service import record_audit_event
from app.services.pdf_generator import (
    generate_previous_approval_pdf,
    generate_affidavit_pdf,
    generate_faculty_list_pdf,
    generate_noc_pdf,
    generate_accreditation_pdf,
    generate_infrastructure_pdf,
    generate_payment_receipt_pdf
)


def seed_database(drop_existing: bool = False):
    print("Verifying database schema...")
    if drop_existing:
        print("Dropping and recreating database tables (--drop specified)...")
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.SYNTHETIC_DATA_DIR, exist_ok=True)

    try:
        user_count = db.query(User).count()
        if user_count > 0 and not drop_existing:
            print(f"Database already contains {user_count} users. Preserving existing data and skipping seed.")
            db.close()
            return
    except Exception as e:
        print(f"Note on existing tables check: {e}. Proceeding with seed.")

    print("1. Seeding Users...")
    users = [
        User(
            username="institution_demo",
            email="principal@ditm.edu.in",
            hashed_password=get_password_hash("password123"),
            full_name="Dr. Alok Verma (Principal)",
            role=UserRole.INSTITUTION,
            institution_id="1-1092837482"
        ),
        User(
            username="reviewer_demo",
            email="scrutiny.officer@aicte.gov.in",
            hashed_password=get_password_hash("password123"),
            full_name="Er. Suresh Menon (Scrutiny Officer)",
            role=UserRole.REVIEWER
        ),
        User(
            username="admin_demo",
            email="admin@aicte.gov.in",
            hashed_password=get_password_hash("password123"),
            full_name="Director S. K. Aggarwal (Regulatory Admin)",
            role=UserRole.ADMIN
        )
    ]
    for u in users:
        db.add(u)
    db.commit()

    print("2. Seeding Master Checklist Rules...")
    checklist_rules = [
        ChecklistRule(
            rule_code="CHK-EOA-01",
            category="EXTENSION_OF_APPROVAL",
            document_type="PREVIOUS_APPROVAL",
            requirement_name="Previous Year AICTE Approval Letter (EoA)",
            description="Copy of the latest Extension of Approval letter issued by the Council for academic continuity.",
            is_required=True,
            is_active=True
        ),
        ChecklistRule(
            rule_code="CHK-EOA-02",
            category="EXTENSION_OF_APPROVAL",
            document_type="AFFIDAVIT",
            requirement_name="Statutory Affidavit (Format-1) on Non-Judicial Stamp",
            description="Affidavit submitted by Chairman/Secretary stating compliance with all faculty, infrastructure, and anti-ragging norms.",
            is_required=True,
            is_active=True
        ),
        ChecklistRule(
            rule_code="CHK-EOA-03",
            category="EXTENSION_OF_APPROVAL",
            document_type="FACULTY_LIST",
            requirement_name="Faculty Details & Cadre Ratio Certification",
            description="Consolidated list of teaching faculty including cadre ratio (1:20 or 1:15) and Ph.D qualifications.",
            is_required=True,
            is_active=True
        ),
        ChecklistRule(
            rule_code="CHK-EOA-04",
            category="EXTENSION_OF_APPROVAL",
            document_type="NOC",
            requirement_name="State Government & Affiliating University NOC",
            description="Valid No Objection Certificate or continuation of affiliation for the requested academic session.",
            is_required=True,
            is_active=True
        ),
        ChecklistRule(
            rule_code="CHK-EOA-05",
            category="EXTENSION_OF_APPROVAL",
            document_type="INFRASTRUCTURE_EVIDENCE",
            requirement_name="Land Area & Instructional Built-Up Area Proof",
            description="Architect certificate validating barrier-free instructional space and requisite contiguous campus land.",
            is_required=True,
            is_active=True
        ),
        ChecklistRule(
            rule_code="CHK-EOA-06",
            category="EXTENSION_OF_APPROVAL",
            document_type="PAYMENT_RECEIPT",
            requirement_name="Technical Education Regulatory (TER) Payment Receipt",
            description="Official receipt confirming regulatory processing fee deposit through the AICTE national portal.",
            is_required=True,
            is_active=True
        ),
        ChecklistRule(
            rule_code="CHK-EOA-07",
            category="INCREASE_IN_INTAKE",
            document_type="ACCREDITATION_CERT",
            requirement_name="National Board of Accreditation (NBA) Certificate",
            description="Mandatory valid Tier-I/II NBA accreditation certificate required for expansion in sanctioned student intake.",
            is_required=True,
            is_active=True
        )
    ]
    for cr in checklist_rules:
        db.add(cr)
    db.commit()

    print("3. Seeding Master Compliance Rules...")
    compliance_rules = [
        ComplianceRule(
            rule_id="R-AICTE-EOA-PREV-01",
            rule_name="Previous Approval Validity & Intake Continuity",
            description="Verifies that the institution possesses a valid prior approval letter and intake matches declared baseline.",
            category_condition="ALL",
            required_evidence_type="PREVIOUS_APPROVAL",
            evaluation_logic="PREVIOUS_APPROVAL_VALIDITY",
            severity=ComplianceRuleSeverity.HIGH
        ),
        ComplianceRule(
            rule_id="R-AICTE-EOA-AFF-02",
            rule_name="Statutory Affidavit and Notarized Undertaking",
            description="Validates submission of duly executed statutory Format-1 affidavit with notary reference number.",
            category_condition="ALL",
            required_evidence_type="AFFIDAVIT",
            evaluation_logic="AFFIDAVIT_COMPLIANCE",
            severity=ComplianceRuleSeverity.HIGH
        ),
        ComplianceRule(
            rule_id="R-AICTE-EOA-FAC-03",
            rule_name="Faculty Cadre Ratio and Student Ratio Compliance",
            description="Enforces mandatory 1:20 teacher-student ratio for undergraduate technical programs.",
            category_condition="ALL",
            required_evidence_type="FACULTY_LIST",
            evaluation_logic="FACULTY_CADRE_RATIO",
            severity=ComplianceRuleSeverity.HIGH
        ),
        ComplianceRule(
            rule_id="R-AICTE-EOA-NOC-04",
            rule_name="State Government and University Affiliation NOC",
            description="Validates active regulatory permission from state technical education directorate and affiliating university.",
            category_condition="ALL",
            required_evidence_type="NOC",
            evaluation_logic="NOC_VALIDITY",
            severity=ComplianceRuleSeverity.HIGH
        ),
        ComplianceRule(
            rule_id="R-AICTE-EOA-INFRA-05",
            rule_name="Campus Built-up Area and Infrastructure Norms",
            description="Requires minimum 4,000 sqm instructional and administrative built-up area for technical colleges.",
            category_condition="ALL",
            required_evidence_type="INFRASTRUCTURE_EVIDENCE",
            evaluation_logic="INFRASTRUCTURE_NORMS",
            severity=ComplianceRuleSeverity.MEDIUM
        ),
        ComplianceRule(
            rule_id="R-AICTE-EOA-TER-06",
            rule_name="TER Regulatory Processing Fee Verification",
            description="Verifies complete payment of required processing charges on the payment gateway.",
            category_condition="ALL",
            required_evidence_type="PAYMENT_RECEIPT",
            evaluation_logic="TER_PAYMENT_STATUS",
            severity=ComplianceRuleSeverity.MEDIUM
        ),
        ComplianceRule(
            rule_id="R-AICTE-INTAKE-EXP-07",
            rule_name="Accreditation Prerequisite for Sanctioned Intake Expansion",
            description="Mandates valid NBA accreditation certificate for institutions seeking intake expansion beyond base quota.",
            category_condition="ALL",
            required_evidence_type="ACCREDITATION_CERT",
            evaluation_logic="ACCREDITATION_EXPANSION_CHECK",
            severity=ComplianceRuleSeverity.CRITICAL
        )
    ]
    for comp in compliance_rules:
        db.add(comp)
    db.commit()

    print("4. Seeding Synthetic Institutional Registry Records...")
    synth_records = [
        SyntheticInstitutionRecord(
            institution_id="1-1092837482",
            institution_name="Delhi Institute of Technology & Management",
            approved_academic_year="2025-26",
            approved_programme="ENGINEERING_AND_TECHNOLOGY",
            approved_course="Computer Science and Engineering",
            approved_intake=120,
            land_area_acres=5.2,
            built_up_area_sqm=12500.0,
            affiliating_university="Guru Gobind Singh Indraprastha University",
            state="Delhi"
        ),
        SyntheticInstitutionRecord(
            institution_id="1-2039485761",
            institution_name="Vanguard College of Engineering",
            approved_academic_year="2025-26",
            approved_programme="ENGINEERING_AND_TECHNOLOGY",
            approved_course="Information Technology",
            approved_intake=60,
            land_area_acres=4.8,
            built_up_area_sqm=9800.0,
            affiliating_university="Anna University",
            state="Tamil Nadu"
        ),
        SyntheticInstitutionRecord(
            institution_id="1-3394857210",
            institution_name="Narmada Valley Institute of Technology",
            approved_academic_year="2025-26",
            approved_programme="ENGINEERING_AND_TECHNOLOGY",
            approved_course="Mechanical Engineering",
            approved_intake=120,
            land_area_acres=6.0,
            built_up_area_sqm=11000.0,
            affiliating_university="Rajiv Gandhi Proudyogiki Vishwavidyalaya",
            state="Madhya Pradesh"
        ),
        SyntheticInstitutionRecord(
            institution_id="1-4491827365",
            institution_name="Apex Institute of Advanced Engineering",
            approved_academic_year="2025-26",
            approved_programme="ENGINEERING_AND_TECHNOLOGY",
            approved_course="Computer Science and Engineering",
            approved_intake=120, # Application claims 180!
            land_area_acres=5.5,
            built_up_area_sqm=14000.0,
            affiliating_university="Visvesvaraya Technological University",
            state="Karnataka"
        ),
        SyntheticInstitutionRecord(
            institution_id="1-5582910473",
            institution_name="Kalinga Technical University College",
            approved_academic_year="2025-26",
            approved_programme="ENGINEERING_AND_TECHNOLOGY",
            approved_course="Electronics and Communication",
            approved_intake=120, # Discrepancy with application
            land_area_acres=7.1,
            built_up_area_sqm=15200.0,
            affiliating_university="Biju Patnaik University of Technology",
            state="Odisha"
        ),
        SyntheticInstitutionRecord(
            institution_id="1-6673829104",
            institution_name="Shivalik Institute of Engineering & Technology",
            approved_academic_year="2025-26",
            approved_programme="ENGINEERING_AND_TECHNOLOGY",
            approved_course="Civil Engineering",
            approved_intake=60,
            land_area_acres=5.0,
            built_up_area_sqm=8900.0,
            affiliating_university="IK Gujral Punjab Technical University",
            state="Punjab"
        ),
        SyntheticInstitutionRecord(
            institution_id="1-7784920193",
            institution_name="Greenfield Engineering College",
            approved_academic_year="2025-26",
            approved_programme="ENGINEERING_AND_TECHNOLOGY",
            approved_course="Computer Science and Engineering",
            approved_intake=120,
            land_area_acres=5.0,
            built_up_area_sqm=10500.0,
            affiliating_university="Jawaharlal Nehru Technological University",
            state="Telangana"
        ),
        SyntheticInstitutionRecord(
            institution_id="1-8895031284",
            institution_name="Heritage Institute of Technology",
            approved_academic_year="2025-26",
            approved_programme="ENGINEERING_AND_TECHNOLOGY",
            approved_course="Computer Science and Engineering",
            approved_intake=60,
            land_area_acres=4.2,
            built_up_area_sqm=7500.0,
            affiliating_university="Maulana Abul Kalam Azad University of Technology",
            state="West Bengal"
        )
    ]
    for sr in synth_records:
        db.add(sr)
    db.commit()

    print("5. Seeding Mock Authority Registry...")
    mock_auth_records = [
        MockAuthorityRecord(
            authority_name="STATE_TECHNICAL_BOARD_MOCK",
            certificate_number="NOC-2025-99882",
            institution_id="1-1092837482",
            institution_name="Delhi Institute of Technology & Management",
            doc_type="NOC",
            issue_date="2025-06-20",
            expiry_date="2027-07-31",
            status="VALID",
            is_simulated=True
        ),
        MockAuthorityRecord(
            authority_name="STATE_TECHNICAL_BOARD_MOCK",
            certificate_number="NOC-MP-2023-EXPIRED",
            institution_id="1-3394857210",
            institution_name="Narmada Valley Institute of Technology",
            doc_type="NOC",
            issue_date="2023-01-10",
            expiry_date="2024-03-15",
            status="EXPIRED",
            is_simulated=True
        ),
        MockAuthorityRecord(
            authority_name="ACCREDITATION_BOARD_MOCK",
            certificate_number="NBA-TIER1-4491",
            institution_id="1-1092837482",
            institution_name="Delhi Institute of Technology & Management",
            doc_type="ACCREDITATION_CERT",
            issue_date="2025-07-01",
            expiry_date="2028-06-30",
            status="VALID",
            is_simulated=True
        ),
        MockAuthorityRecord(
            authority_name="STATE_TECHNICAL_BOARD_MOCK",
            certificate_number="NOC-TEL-2025-MISMATCH",
            institution_id="1-9999999999", # Intentionally points to different college
            institution_name="Southern Telangana Academy of Sciences",
            doc_type="NOC",
            issue_date="2025-05-10",
            expiry_date="2027-05-09",
            status="VALID",
            is_simulated=True
        )
    ]
    for mar in mock_auth_records:
        db.add(mar)
    db.commit()

    print("6. Generating 8 Synthetic Demonstration Applications...")
    
    # Helper to create document and attach to application
    def attach_document(app_id, filepath, doc_type_hint=None):
        filename = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            content = f.read()
        sha256 = hashlib.sha256(content).hexdigest()
        stored_name = f"seed_{sha256[:12]}_{filename}"
        dest_path = os.path.join(settings.UPLOAD_DIR, stored_name)
        shutil.copyfile(filepath, dest_path)
        
        # OCR extraction
        res = ocr_service.extract_from_file(dest_path, "application/pdf")
        doc_type, conf, method = classifier_service.classify(res.full_text, filename)
        if doc_type_hint:
            doc_type = doc_type_hint

        doc = Document(
            id=f"DOC-{uuid.uuid4().hex[:8].upper()}",
            application_id=app_id,
            original_filename=filename,
            stored_filename=stored_name,
            file_path=dest_path,
            file_size_bytes=len(content),
            mime_type="application/pdf",
            sha256_hash=sha256,
            doc_type=doc_type,
            classification_confidence=conf,
            classification_method=method,
            ocr_status=OCRStatus.COMPLETED,
            ocr_engine_used=res.engine_used,
            extracted_text=res.full_text,
            page_count=res.page_count
        )
        db.add(doc)
        db.commit()

        # Extract fields
        extracted = extraction_service.extract_fields(res.full_text, res.page_texts, doc_type)
        for ef in extracted:
            fld = ExtractedField(
                document_id=doc.id,
                application_id=app_id,
                field_name=ef.field_name,
                extracted_value=ef.extracted_value,
                normalized_value=ef.normalized_value,
                page_number=ef.page_number,
                confidence=ef.confidence,
                snippet=ef.snippet
            )
            db.add(fld)
        db.commit()

        # Update checklist item
        chk = db.query(ApplicationChecklistItem).filter(
            ApplicationChecklistItem.application_id == app_id,
            ApplicationChecklistItem.document_type == doc_type.value
        ).first()
        if chk:
            chk.is_submitted = True
            chk.document_id = doc.id
            chk.validation_status = "SATISFIED"
            chk.explanation = f"Submitted as {filename}"
        db.commit()

        return doc

    # --- Case 1: APP-2026-0001 (Clean Application) ---
    print(" -> Seeding Scenario 1: Clean Application (APP-2026-0001)...")
    app1 = Application(
        id="APP-2026-0001",
        institution_id="1-1092837482",
        institution_name="Delhi Institute of Technology & Management",
        category=ApplicationCategory.EXTENSION_OF_APPROVAL,
        academic_year="2026-27",
        programme="ENGINEERING_AND_TECHNOLOGY",
        course_name="Computer Science and Engineering",
        existing_intake=120,
        requested_intake=120,
        contact_person="Dr. Alok Verma",
        contact_email="principal@ditm.edu.in",
        contact_phone="+91-9810123456",
        status=ApplicationStatus.SUBMITTED,
        validation_status=ValidationOverallStatus.NOT_EVALUATED,
        submission_date=datetime.utcnow()
    )
    db.add(app1)
    db.commit()
    # Init checklist
    for r in checklist_rules:
        if r.category in ["ALL", "EXTENSION_OF_APPROVAL"]:
            db.add(ApplicationChecklistItem(
                application_id=app1.id,
                rule_code=r.rule_code,
                requirement_name=r.requirement_name,
                document_type=r.document_type,
                is_required=r.is_required,
                is_submitted=False,
                validation_status="MISSING"
            ))
    db.commit()

    # Generate test documents
    p1 = os.path.join(settings.SYNTHETIC_DATA_DIR, "app1_eoa.pdf")
    generate_previous_approval_pdf(p1, app1.institution_name, app1.institution_id, 120, app1.course_name)
    attach_document(app1.id, p1, DocumentType.PREVIOUS_APPROVAL)

    p2 = os.path.join(settings.SYNTHETIC_DATA_DIR, "app1_affidavit.pdf")
    generate_affidavit_pdf(p2, app1.institution_name, app1.institution_id)
    attach_document(app1.id, p2, DocumentType.AFFIDAVIT)

    p3 = os.path.join(settings.SYNTHETIC_DATA_DIR, "app1_faculty.pdf")
    generate_faculty_list_pdf(p3, app1.institution_name, app1.institution_id, 36, 12)
    attach_document(app1.id, p3, DocumentType.FACULTY_LIST)

    p4 = os.path.join(settings.SYNTHETIC_DATA_DIR, "app1_noc.pdf")
    generate_noc_pdf(p4, app1.institution_name, app1.institution_id, cert_no="NOC-2025-99882", valid_till="31/07/2027")
    noc_doc1 = attach_document(app1.id, p4, DocumentType.NOC)

    p5 = os.path.join(settings.SYNTHETIC_DATA_DIR, "app1_infra.pdf")
    generate_infrastructure_pdf(p5, app1.institution_name, app1.institution_id, 5.2, 12500)
    attach_document(app1.id, p5, DocumentType.INFRASTRUCTURE_EVIDENCE)

    p6 = os.path.join(settings.SYNTHETIC_DATA_DIR, "app1_ter.pdf")
    generate_payment_receipt_pdf(p6, app1.institution_name, app1.institution_id, "TXN-AICTE-10001", "150000")
    attach_document(app1.id, p6, DocumentType.PAYMENT_RECEIPT)

    # Pre-verify NOC
    db.add(VerificationResult(
        application_id=app1.id,
        document_id=noc_doc1.id,
        authority_name="STATE_TECHNICAL_BOARD_MOCK",
        certificate_number="NOC-2025-99882",
        status=VerificationStatus.VERIFIED,
        is_simulated=True
    ))
    db.commit()

    validation_engine.run_validation(db, app1.id)
    compliance_engine.evaluate_compliance(db, app1.id)

    # --- Case 2: APP-2026-0002 (Missing Required Document) ---
    print(" -> Seeding Scenario 2: Missing Required Document (APP-2026-0002)...")
    app2 = Application(
        id="APP-2026-0002",
        institution_id="1-2039485761",
        institution_name="Vanguard College of Engineering",
        category=ApplicationCategory.EXTENSION_OF_APPROVAL,
        existing_intake=60,
        requested_intake=60,
        contact_person="Dr. K. Ramanathan",
        contact_email="principal@vanguard.ac.in",
        contact_phone="+91-9444123456",
        status=ApplicationStatus.SUBMITTED,
        validation_status=ValidationOverallStatus.NOT_EVALUATED
    )
    db.add(app2)
    db.commit()
    for r in checklist_rules:
        if r.category in ["ALL", "EXTENSION_OF_APPROVAL"]:
            db.add(ApplicationChecklistItem(
                application_id=app2.id,
                rule_code=r.rule_code,
                requirement_name=r.requirement_name,
                document_type=r.document_type,
                is_required=r.is_required,
                is_submitted=False,
                validation_status="MISSING"
            ))
    db.commit()
    p2_1 = os.path.join(settings.SYNTHETIC_DATA_DIR, "app2_eoa.pdf")
    generate_previous_approval_pdf(p2_1, app2.institution_name, app2.institution_id, 60, "Information Technology")
    attach_document(app2.id, p2_1, DocumentType.PREVIOUS_APPROVAL)

    p2_2 = os.path.join(settings.SYNTHETIC_DATA_DIR, "app2_affidavit.pdf")
    generate_affidavit_pdf(p2_2, app2.institution_name, app2.institution_id)
    attach_document(app2.id, p2_2, DocumentType.AFFIDAVIT)

    validation_engine.run_validation(db, app2.id)
    compliance_engine.evaluate_compliance(db, app2.id)

    # --- Case 3: APP-2026-0003 (Expired Document) ---
    print(" -> Seeding Scenario 3: Expired Document (APP-2026-0003)...")
    app3 = Application(
        id="APP-2026-0003",
        institution_id="1-3394857210",
        institution_name="Narmada Valley Institute of Technology",
        category=ApplicationCategory.EXTENSION_OF_APPROVAL,
        existing_intake=120,
        requested_intake=120,
        contact_person="Prof. N. K. Tiwari",
        contact_email="registrar@nvit.org",
        contact_phone="+91-9826012345",
        status=ApplicationStatus.SUBMITTED
    )
    db.add(app3)
    db.commit()
    for r in checklist_rules:
        if r.category in ["ALL", "EXTENSION_OF_APPROVAL"]:
            db.add(ApplicationChecklistItem(
                application_id=app3.id,
                rule_code=r.rule_code,
                requirement_name=r.requirement_name,
                document_type=r.document_type,
                is_required=r.is_required,
                is_submitted=False,
                validation_status="MISSING"
            ))
    db.commit()
    p3_1 = os.path.join(settings.SYNTHETIC_DATA_DIR, "app3_eoa.pdf")
    generate_previous_approval_pdf(p3_1, app3.institution_name, app3.institution_id, 120, "Mechanical Engineering")
    attach_document(app3.id, p3_1, DocumentType.PREVIOUS_APPROVAL)

    p3_2 = os.path.join(settings.SYNTHETIC_DATA_DIR, "app3_noc_expired.pdf")
    generate_noc_pdf(p3_2, app3.institution_name, app3.institution_id, state_name="Madhya Pradesh", cert_no="NOC-MP-2023-EXPIRED", issue_date="10/01/2023", valid_till="15/03/2024")
    attach_document(app3.id, p3_2, DocumentType.NOC)

    validation_engine.run_validation(db, app3.id)
    compliance_engine.evaluate_compliance(db, app3.id)

    # --- Case 4: APP-2026-0004 (Application / Document Field Mismatch) ---
    print(" -> Seeding Scenario 4: Field Mismatch (APP-2026-0004)...")
    app4 = Application(
        id="APP-2026-0004",
        institution_id="1-4491827365",
        institution_name="Apex Institute of Advanced Engineering",
        category=ApplicationCategory.EXTENSION_OF_APPROVAL,
        existing_intake=180, # Mismatch: Application claims 180, but letter says 120!
        requested_intake=180,
        contact_person="Dr. B. R. Patil",
        contact_email="dean@apexinstitute.edu.in",
        contact_phone="+91-9845012345",
        status=ApplicationStatus.SUBMITTED
    )
    db.add(app4)
    db.commit()
    for r in checklist_rules:
        if r.category in ["ALL", "EXTENSION_OF_APPROVAL"]:
            db.add(ApplicationChecklistItem(
                application_id=app4.id,
                rule_code=r.rule_code,
                requirement_name=r.requirement_name,
                document_type=r.document_type,
                is_required=r.is_required,
                is_submitted=False,
                validation_status="MISSING"
            ))
    db.commit()
    p4_1 = os.path.join(settings.SYNTHETIC_DATA_DIR, "app4_eoa_120.pdf")
    generate_previous_approval_pdf(p4_1, app4.institution_name, app4.institution_id, 120, "Computer Science and Engineering")
    attach_document(app4.id, p4_1, DocumentType.PREVIOUS_APPROVAL)

    validation_engine.run_validation(db, app4.id)
    compliance_engine.evaluate_compliance(db, app4.id)

    # --- Case 5: APP-2026-0005 (Synthetic Institutional Record Mismatch) ---
    print(" -> Seeding Scenario 5: Institutional Record Mismatch (APP-2026-0005)...")
    app5 = Application(
        id="APP-2026-0005",
        institution_id="1-5582910473",
        institution_name="Kalinga Technical University College",
        category=ApplicationCategory.EXTENSION_OF_APPROVAL,
        existing_intake=240, # Discrepancy with official master record which has 120
        requested_intake=240,
        contact_person="Prof. S. C. Mohanty",
        contact_email="principal@ktuc.ac.in",
        contact_phone="+91-9937012345",
        status=ApplicationStatus.SUBMITTED
    )
    db.add(app5)
    db.commit()
    for r in checklist_rules:
        if r.category in ["ALL", "EXTENSION_OF_APPROVAL"]:
            db.add(ApplicationChecklistItem(
                application_id=app5.id,
                rule_code=r.rule_code,
                requirement_name=r.requirement_name,
                document_type=r.document_type,
                is_required=r.is_required,
                is_submitted=False,
                validation_status="MISSING"
            ))
    db.commit()
    p5_1 = os.path.join(settings.SYNTHETIC_DATA_DIR, "app5_eoa.pdf")
    generate_previous_approval_pdf(p5_1, app5.institution_name, app5.institution_id, 240, "Electronics and Communication")
    attach_document(app5.id, p5_1, DocumentType.PREVIOUS_APPROVAL)

    validation_engine.run_validation(db, app5.id)
    compliance_engine.evaluate_compliance(db, app5.id)

    # --- Case 6: APP-2026-0006 (Duplicate Document) ---
    print(" -> Seeding Scenario 6: Duplicate Document Detection (APP-2026-0006)...")
    app6 = Application(
        id="APP-2026-0006",
        institution_id="1-6673829104",
        institution_name="Shivalik Institute of Engineering & Technology",
        category=ApplicationCategory.EXTENSION_OF_APPROVAL,
        existing_intake=60,
        requested_intake=60,
        contact_person="Dr. Harpreet Singh",
        contact_email="director@shivalik.edu",
        contact_phone="+91-9876543210",
        status=ApplicationStatus.SUBMITTED
    )
    db.add(app6)
    db.commit()
    for r in checklist_rules:
        if r.category in ["ALL", "EXTENSION_OF_APPROVAL"]:
            db.add(ApplicationChecklistItem(
                application_id=app6.id,
                rule_code=r.rule_code,
                requirement_name=r.requirement_name,
                document_type=r.document_type,
                is_required=r.is_required,
                is_submitted=False,
                validation_status="MISSING"
            ))
    db.commit()
    p6_orig = os.path.join(settings.SYNTHETIC_DATA_DIR, "app6_affidavit_original.pdf")
    generate_affidavit_pdf(p6_orig, app6.institution_name, app6.institution_id)
    attach_document(app6.id, p6_orig, DocumentType.AFFIDAVIT)

    # Duplicate file uploaded under different filename for faculty
    p6_dup = os.path.join(settings.SYNTHETIC_DATA_DIR, "app6_faculty_list_duplicate.pdf")
    shutil.copyfile(p6_orig, p6_dup)
    attach_document(app6.id, p6_dup, DocumentType.FACULTY_LIST)

    validation_engine.run_validation(db, app6.id)
    compliance_engine.evaluate_compliance(db, app6.id)

    # --- Case 7: APP-2026-0007 (Mock Authority Verification Mismatch) ---
    print(" -> Seeding Scenario 7: Mock Authority Verification Mismatch (APP-2026-0007)...")
    app7 = Application(
        id="APP-2026-0007",
        institution_id="1-7784920193",
        institution_name="Greenfield Engineering College",
        category=ApplicationCategory.EXTENSION_OF_APPROVAL,
        existing_intake=120,
        requested_intake=120,
        contact_person="Dr. M. S. Reddy",
        contact_email="principal@greenfield.edu",
        contact_phone="+91-9849012345",
        status=ApplicationStatus.SUBMITTED
    )
    db.add(app7)
    db.commit()
    for r in checklist_rules:
        if r.category in ["ALL", "EXTENSION_OF_APPROVAL"]:
            db.add(ApplicationChecklistItem(
                application_id=app7.id,
                rule_code=r.rule_code,
                requirement_name=r.requirement_name,
                document_type=r.document_type,
                is_required=r.is_required,
                is_submitted=False,
                validation_status="MISSING"
            ))
    db.commit()
    p7_noc = os.path.join(settings.SYNTHETIC_DATA_DIR, "app7_noc_mismatch.pdf")
    generate_noc_pdf(p7_noc, app7.institution_name, app7.institution_id, state_name="Telangana", cert_no="NOC-TEL-2025-MISMATCH")
    doc7 = attach_document(app7.id, p7_noc, DocumentType.NOC)

    # Trigger authority check which reveals institution ID discrepancy in authority records
    db.add(VerificationResult(
        application_id=app7.id,
        document_id=doc7.id,
        authority_name="STATE_TECHNICAL_BOARD_MOCK",
        certificate_number="NOC-TEL-2025-MISMATCH",
        status=VerificationStatus.MISMATCH_DETECTED,
        is_simulated=True,
        mismatch_details="Institution ID mismatch: Submitted '1-7784920193' vs Authority Record '1-9999999999' (Southern Telangana Academy of Sciences)"
    ))
    db.commit()

    validation_engine.run_validation(db, app7.id)
    compliance_engine.evaluate_compliance(db, app7.id)

    # --- Case 8: APP-2026-0008 (Multiple Findings & Deficiency Inquiry) ---
    print(" -> Seeding Scenario 8: Multiple Findings & Inquiries (APP-2026-0008)...")
    app8 = Application(
        id="APP-2026-0008",
        institution_id="1-8895031284",
        institution_name="Heritage Institute of Technology",
        category=ApplicationCategory.INCREASE_IN_INTAKE,
        existing_intake=60,
        requested_intake=180, # > 50% jump without NBA accreditation!
        contact_person="Prof. D. K. Banerjee",
        contact_email="principal@heritage-tech.edu",
        contact_phone="+91-9830012345",
        status=ApplicationStatus.DEFICIENCIES_COMMUNICATED
    )
    db.add(app8)
    db.commit()
    for r in checklist_rules:
        if r.category in ["ALL", "INCREASE_IN_INTAKE"]:
            db.add(ApplicationChecklistItem(
                application_id=app8.id,
                rule_code=r.rule_code,
                requirement_name=r.requirement_name,
                document_type=r.document_type,
                is_required=r.is_required,
                is_submitted=False,
                validation_status="MISSING"
            ))
    db.commit()
    p8_1 = os.path.join(settings.SYNTHETIC_DATA_DIR, "app8_eoa.pdf")
    generate_previous_approval_pdf(p8_1, app8.institution_name, app8.institution_id, 60, "Computer Science and Engineering")
    attach_document(app8.id, p8_1, DocumentType.PREVIOUS_APPROVAL)

    p8_2 = os.path.join(settings.SYNTHETIC_DATA_DIR, "app8_fac_deficient.pdf")
    # Severely deficient faculty (only 6 faculty for requested 180 seats)
    generate_faculty_list_pdf(p8_2, app8.institution_name, app8.institution_id, total_faculty=6, phd_faculty=1)
    attach_document(app8.id, p8_2, DocumentType.FACULTY_LIST)

    p8_3 = os.path.join(settings.SYNTHETIC_DATA_DIR, "app8_noc_expired.pdf")
    generate_noc_pdf(p8_3, app8.institution_name, app8.institution_id, state_name="West Bengal", valid_till="10/12/2023")
    attach_document(app8.id, p8_3, DocumentType.NOC)

    validation_engine.run_validation(db, app8.id)
    compliance_engine.evaluate_compliance(db, app8.id)

    # Seed an open evidence request
    fac_finding = db.query(ValidationFinding).filter(
        ValidationFinding.application_id == app8.id,
        ValidationFinding.category == FindingCategory.INTAKE_INCONSISTENCY
    ).first()

    db.add(EvidenceRequest(
        id="REQ-2026-DEMO01",
        application_id=app8.id,
        finding_id=fac_finding.id if fac_finding else None,
        requested_by="reviewer_demo",
        request_text="Please submit valid NBA Tier-I/II accreditation certificate justifying the requested intake increase from 60 to 180 seats.",
        status=EvidenceRequestStatus.PENDING,
        requested_at=datetime.utcnow()
    ))
    db.commit()

    print("7. Seeding Initial Audit Trail Events...")
    record_audit_event(
        db=db,
        actor_id="SYSTEM_INIT",
        actor_role="SYSTEM",
        action="SYSTEM_INITIALIZED",
        entity_type="SYSTEM",
        entity_id="GLOBAL",
        details="Prototype initialized and 8 demonstration scenarios loaded."
    )

    db.close()
    print("Seeding completed successfully! All 8 demonstration scenarios are ready.")


if __name__ == "__main__":
    drop = "--drop" in sys.argv or "--force" in sys.argv
    seed_database(drop_existing=drop)
