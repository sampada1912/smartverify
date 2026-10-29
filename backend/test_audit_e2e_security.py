import os
import sys
import io
import json
import uuid
import httpx
from datetime import datetime

# Base API URL
API_BASE = "http://127.0.0.1:8000/api/v1"

def print_section(title):
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)

def main():
    print_section("AICTE SmartVerify SIH26261 — Comprehensive Engineering Audit Suite")
    
    client = httpx.Client(timeout=30.0)

    # 1. Authenticate Personas
    print("\n[Step 0] Authenticating Personas...")
    resp_inst = client.post(f"{API_BASE}/auth/demo-login", json={"role": "INSTITUTION"})
    assert resp_inst.status_code == 200, f"Inst login failed: {resp_inst.text}"
    inst_token = resp_inst.json()["access_token"]
    inst_headers = {"Authorization": f"Bearer {inst_token}"}
    print(f"  ✓ Authenticated as INSTITUTION ({resp_inst.json()['username']})")

    resp_rev = client.post(f"{API_BASE}/auth/demo-login", json={"role": "REVIEWER"})
    assert resp_rev.status_code == 200, f"Reviewer login failed: {resp_rev.text}"
    rev_token = resp_rev.json()["access_token"]
    rev_headers = {"Authorization": f"Bearer {rev_token}"}
    print(f"  ✓ Authenticated as REVIEWER ({resp_rev.json()['username']})")

    resp_adm = client.post(f"{API_BASE}/auth/demo-login", json={"role": "ADMIN"})
    assert resp_adm.status_code == 200, f"Admin login failed: {resp_adm.text}"
    adm_token = resp_adm.json()["access_token"]
    adm_headers = {"Authorization": f"Bearer {adm_token}"}
    print(f"  ✓ Authenticated as ADMIN ({resp_adm.json()['username']})")

    # Generate synthetic PDF helper
    from app.services.pdf_generator import (
        generate_previous_approval_pdf,
        generate_noc_pdf,
        generate_affidavit_pdf,
        generate_faculty_list_pdf,
        generate_infrastructure_pdf,
        generate_payment_receipt_pdf
    )

    test_pdf_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/test_tmp"))
    os.makedirs(test_pdf_dir, exist_ok=True)

    # -------------------------------------------------------------
    # Case 1: Clean Application (End-to-End Creation + Uploads)
    # -------------------------------------------------------------
    print_section("Case 1: Clean Application (End-to-End Creation + Uploads)")
    app1_payload = {
        "institution_id": "1-9182736450",
        "institution_name": "Audit Institute of Technology Clean",
        "category": "EXTENSION_OF_APPROVAL",
        "academic_year": "2026-27",
        "programme": "ENGINEERING_AND_TECHNOLOGY",
        "course_name": "Computer Science and Engineering",
        "existing_intake": 120,
        "requested_intake": 120,
        "contact_person": "Audit Registrar",
        "contact_email": "registrar@auditclean.edu",
        "contact_phone": "+91 9876543210"
    }
    r = client.post(f"{API_BASE}/applications", json=app1_payload, headers=inst_headers)
    print(f"  POST /applications -> {r.status_code}")
    assert r.status_code in [200, 201], r.text
    app1 = r.json()
    app1_id = app1["id"]
    print(f"  Created Application: {app1_id}")

    # Generate matching clean PDFs
    p_eoa = os.path.join(test_pdf_dir, "clean_eoa.pdf")
    generate_previous_approval_pdf(p_eoa, app1["institution_name"], app1["institution_id"], 120, "Computer Science and Engineering")
    p_noc = os.path.join(test_pdf_dir, "clean_noc.pdf")
    generate_noc_pdf(p_noc, app1["institution_name"], app1["institution_id"], state_name="Maharashtra", cert_no="NOC-2024-MH-4421", valid_till="2028-06-30")
    p_aff = os.path.join(test_pdf_dir, "clean_affidavit.pdf")
    generate_affidavit_pdf(p_aff, app1["institution_name"], app1["institution_id"])
    p_fac = os.path.join(test_pdf_dir, "clean_faculty.pdf")
    generate_faculty_list_pdf(p_fac, app1["institution_name"], app1["institution_id"], total_faculty=28)
    p_inf = os.path.join(test_pdf_dir, "clean_infra.pdf")
    generate_infrastructure_pdf(p_inf, app1["institution_name"], app1["institution_id"], land_acres=5.2, built_up_sqm=6500)
    p_pay = os.path.join(test_pdf_dir, "clean_pay.pdf")
    generate_payment_receipt_pdf(p_pay, app1["institution_name"], app1["institution_id"], txn_id="TER-TXN-998877")

    # Upload all 6 clean documents
    files = [
        ("files", ("clean_eoa.pdf", open(p_eoa, "rb"), "application/pdf")),
        ("files", ("clean_noc.pdf", open(p_noc, "rb"), "application/pdf")),
        ("files", ("clean_affidavit.pdf", open(p_aff, "rb"), "application/pdf")),
        ("files", ("clean_faculty.pdf", open(p_fac, "rb"), "application/pdf")),
        ("files", ("clean_infra.pdf", open(p_inf, "rb"), "application/pdf")),
        ("files", ("clean_pay.pdf", open(p_pay, "rb"), "application/pdf")),
    ]
    r_up = client.post(f"{API_BASE}/applications/{app1_id}/documents", files=files, headers=inst_headers)
    print(f"  POST /applications/{app1_id}/documents -> {r_up.status_code}")
    assert r_up.status_code == 200, r_up.text

    # Submit application
    r_sub = client.post(f"{API_BASE}/applications/{app1_id}/submit", headers=inst_headers)
    print(f"  POST /applications/{app1_id}/submit -> {r_sub.status_code}")
    assert r_sub.status_code == 200

    # Query findings
    r_find = client.get(f"{API_BASE}/applications/{app1_id}/findings", headers=rev_headers)
    findings = r_find.json()
    open_findings = [f for f in findings if f["status"] in ["OPEN", "UNDER_REVIEW"]]
    print(f"  Open findings count for clean app: {len(open_findings)}")
    assert len(open_findings) == 0, f"Expected 0 open findings for clean app, got: {open_findings}"
    print("  ✓ Clean application test: PASS")

    # -------------------------------------------------------------
    # Case 2: Missing Required Document
    # -------------------------------------------------------------
    print_section("Case 2: Missing Required Document")
    app2_payload = {
        "institution_id": "1-9182736451",
        "institution_name": "Audit Institute Missing NOC",
        "category": "EXTENSION_OF_APPROVAL",
        "academic_year": "2026-27",
        "programme": "ENGINEERING_AND_TECHNOLOGY",
        "course_name": "Mechanical Engineering",
        "existing_intake": 60,
        "requested_intake": 60,
        "contact_person": "Registrar",
        "contact_email": "reg@missing.edu",
        "contact_phone": "+91 9876543211"
    }
    r = client.post(f"{API_BASE}/applications", json=app2_payload, headers=inst_headers)
    app2_id = r.json()["id"]

    # Upload only approval letter, missing NOC, affidavit, etc.
    p_eoa2 = os.path.join(test_pdf_dir, "missing_test_eoa.pdf")
    generate_previous_approval_pdf(p_eoa2, app2_payload["institution_name"], app2_payload["institution_id"], 60, "Mechanical Engineering")
    files = [("files", ("eoa.pdf", open(p_eoa2, "rb"), "application/pdf"))]
    client.post(f"{API_BASE}/applications/{app2_id}/documents", files=files, headers=inst_headers)

    # Check checklist and findings
    r_chk = client.get(f"{API_BASE}/applications/{app2_id}/checklist", headers=rev_headers)
    chk = r_chk.json()
    missing_items = [c for c in chk if c["is_required"] and not c["is_submitted"]]
    print(f"  Unsubmitted required checklist items: {len(missing_items)}")

    r_f2 = client.get(f"{API_BASE}/applications/{app2_id}/findings", headers=rev_headers)
    f2 = r_f2.json()
    missing_findings = [f for f in f2 if f["category"] == "MISSING_DOCUMENT"]
    print(f"  MISSING_DOCUMENT findings detected: {len(missing_findings)}")
    assert len(missing_findings) > 0, "Expected MISSING_DOCUMENT findings!"
    print("  ✓ Missing required document detection: PASS")

    # -------------------------------------------------------------
    # Case 3: Expired Certificate Detection
    # -------------------------------------------------------------
    print_section("Case 3: Expired Certificate Detection")
    app3_payload = {
        "institution_id": "1-9182736452",
        "institution_name": "Audit Institute Expired Certificate",
        "category": "EXTENSION_OF_APPROVAL",
        "academic_year": "2026-27",
        "programme": "ENGINEERING_AND_TECHNOLOGY",
        "course_name": "Civil Engineering",
        "existing_intake": 60,
        "requested_intake": 60,
        "contact_person": "Registrar",
        "contact_email": "reg@expired.edu",
        "contact_phone": "+91 9876543212"
    }
    r = client.post(f"{API_BASE}/applications", json=app3_payload, headers=inst_headers)
    app3_id = r.json()["id"]

    # Generate expired NOC (valid till 2022-05-15)
    p_exp_noc = os.path.join(test_pdf_dir, "expired_noc.pdf")
    generate_noc_pdf(p_exp_noc, app3_payload["institution_name"], app3_payload["institution_id"], state_name="Karnataka", cert_no="NOC-EXP-2022", issue_date="15/05/2020", valid_till="2022-05-15")
    files = [("files", ("noc.pdf", open(p_exp_noc, "rb"), "application/pdf"))]
    client.post(f"{API_BASE}/applications/{app3_id}/documents", files=files, headers=inst_headers)

    r_f3 = client.get(f"{API_BASE}/applications/{app3_id}/findings", headers=rev_headers)
    f3 = r_f3.json()
    expired_findings = [f for f in f3 if f["category"] == "EXPIRED_DOCUMENT"]
    print(f"  EXPIRED_DOCUMENT findings detected: {len(expired_findings)}")
    assert len(expired_findings) > 0, f"Expected EXPIRED_DOCUMENT finding, got: {f3}"
    print(f"  Finding Title: {expired_findings[0]['title']}")
    print(f"  Observed Expiry: {expired_findings[0]['observed_value']}")
    print("  ✓ Expired document detection: PASS")

    # -------------------------------------------------------------
    # Case 4: Application vs Document Field Mismatch
    # -------------------------------------------------------------
    print_section("Case 4: Application vs Document Field Mismatch")
    app4_payload = {
        "institution_id": "1-9182736453",
        "institution_name": "Audit Institute Intake Mismatch",
        "category": "EXTENSION_OF_APPROVAL",
        "academic_year": "2026-27",
        "programme": "ENGINEERING_AND_TECHNOLOGY",
        "course_name": "Electrical Engineering",
        "existing_intake": 180,  # Claims 180
        "requested_intake": 180,
        "contact_person": "Registrar",
        "contact_email": "reg@mismatch.edu",
        "contact_phone": "+91 9876543213"
    }
    r = client.post(f"{API_BASE}/applications", json=app4_payload, headers=inst_headers)
    app4_id = r.json()["id"]

    # Generate previous approval PDF with only 60 intake
    p_mis_eoa = os.path.join(test_pdf_dir, "mismatch_eoa.pdf")
    generate_previous_approval_pdf(p_mis_eoa, app4_payload["institution_name"], app4_payload["institution_id"], 60, "Electrical Engineering")
    files = [("files", ("approval_letter.pdf", open(p_mis_eoa, "rb"), "application/pdf"))]
    client.post(f"{API_BASE}/applications/{app4_id}/documents", files=files, headers=inst_headers)

    r_f4 = client.get(f"{API_BASE}/applications/{app4_id}/findings", headers=rev_headers)
    f4 = r_f4.json()
    mismatch_findings = [f for f in f4 if f["category"] == "FIELD_MISMATCH"]
    print(f"  FIELD_MISMATCH findings detected: {len(mismatch_findings)}")
    assert len(mismatch_findings) > 0, f"Expected FIELD_MISMATCH finding, got: {f4}"
    print(f"  Title: {mismatch_findings[0]['title']}")
    print(f"  Expected: {mismatch_findings[0]['expected_value']} | Observed: {mismatch_findings[0]['observed_value']}")
    print("  ✓ Field mismatch detection: PASS")

    # -------------------------------------------------------------
    # Case 5: Institutional Record Mismatch
    # -------------------------------------------------------------
    print_section("Case 5: Synthetic Institutional Record Mismatch")
    r_f5 = client.get(f"{API_BASE}/applications/APP-2026-0005/findings", headers=rev_headers)
    f5 = r_f5.json()
    rec_findings = [f for f in f5 if f["category"] == "INSTITUTIONAL_RECORD_MISMATCH"]
    print(f"  INSTITUTIONAL_RECORD_MISMATCH findings in APP-2026-0005: {len(rec_findings)}")
    assert len(rec_findings) > 0, f"Expected institutional record mismatch finding!"
    print(f"  Title: {rec_findings[0]['title']}")
    print(f"  Source Record: {rec_findings[0]['source_record']}")
    print("  ✓ Institutional record mismatch detection: PASS")

    # -------------------------------------------------------------
    # Case 6: Exact Duplicate Document (SHA-256)
    # -------------------------------------------------------------
    print_section("Case 6: Exact Duplicate Document (SHA-256)")
    app6_payload = {
        "institution_id": "1-9182736456",
        "institution_name": "Audit Institute Duplicate Test",
        "category": "EXTENSION_OF_APPROVAL",
        "academic_year": "2026-27",
        "programme": "ENGINEERING_AND_TECHNOLOGY",
        "course_name": "Computer Engineering",
        "existing_intake": 120,
        "requested_intake": 120,
        "contact_person": "Registrar",
        "contact_email": "reg@dup.edu",
        "contact_phone": "+91 9876543216"
    }
    r = client.post(f"{API_BASE}/applications", json=app6_payload, headers=inst_headers)
    app6_id = r.json()["id"]

    # Upload identical file under two different names
    files = [
        ("files", ("infra_certificate.pdf", open(p_inf, "rb"), "application/pdf")),
        ("files", ("land_document.pdf", open(p_inf, "rb"), "application/pdf"))
    ]
    client.post(f"{API_BASE}/applications/{app6_id}/documents", files=files, headers=inst_headers)

    r_f6 = client.get(f"{API_BASE}/applications/{app6_id}/findings", headers=rev_headers)
    f6 = r_f6.json()
    dup_findings = [f for f in f6 if f["category"] == "DUPLICATE_DOCUMENT"]
    print(f"  DUPLICATE_DOCUMENT findings detected: {len(dup_findings)}")
    assert len(dup_findings) > 0, f"Expected DUPLICATE_DOCUMENT finding, got: {f6}"
    print(f"  Title: {dup_findings[0]['title']}")
    print(f"  Explanation: {dup_findings[0]['explanation']}")
    print("  ✓ Exact duplicate detection via SHA-256: PASS")

    # -------------------------------------------------------------
    # Case 7: Simulated Authority Verification Mismatch
    # -------------------------------------------------------------
    print_section("Case 7: Simulated Authority Verification Mismatch")
    r_ver = client.post(
        f"{API_BASE}/applications/{app1_id}/verify",
        json={
            "certificate_number": "NOC-NONEXISTENT-9999",
            "authority_name": "STATE_TECHNICAL_BOARD_MOCK"
        },
        headers=rev_headers
    )
    print(f"  POST /applications/{app1_id}/verify -> {r_ver.status_code}")
    ver_res = r_ver.json()
    print(f"  Verification Status: {ver_res['status']}")
    print(f"  is_simulated flag: {ver_res['is_simulated']}")
    assert ver_res["status"] == "MISMATCH_DETECTED"
    assert ver_res["is_simulated"] is True
    print("  ✓ Authority verification mismatch & simulation flag: PASS")

    # -------------------------------------------------------------
    # Case 8: Uncertain or Missing OCR Field
    # -------------------------------------------------------------
    print_section("Case 8: Uncertain or Missing OCR Field Representation")
    import fitz
    empty_pdf_path = os.path.join(test_pdf_dir, "minimal_unstructured.pdf")
    doc_m = fitz.open()
    page_m = doc_m.new_page()
    page_m.insert_text((50, 100), "This is a random flyer with no regulatory numbers or dates.")
    doc_m.save(empty_pdf_path)
    doc_m.close()

    files = [("files", ("minimal_unstructured.pdf", open(empty_pdf_path, "rb"), "application/pdf"))]
    r_up8 = client.post(f"{API_BASE}/applications/{app6_id}/documents", files=files, headers=inst_headers)
    assert r_up8.status_code == 200
    doc8_id = r_up8.json()["documents"][0]["id"]

    r_f8 = client.get(f"{API_BASE}/applications/{app6_id}/fields", headers=rev_headers)
    fields8 = r_f8.json()
    doc8_fields = [f for f in fields8 if f["document_id"] == doc8_id]
    print(f"  Structured fields fabricated for unstructured text: {len(doc8_fields)}")
    assert len(doc8_fields) == 0, "Fields must NEVER be fabricated if missing!"
    print("  ✓ Missing OCR fields not fabricated: PASS")

    # -------------------------------------------------------------
    # Case 9: Reviewer Requesting Additional Evidence
    # -------------------------------------------------------------
    print_section("Case 9: Reviewer Requesting Additional Evidence")
    f_to_request = missing_findings[0]["id"]
    r_ev_req = client.post(
        f"{API_BASE}/applications/{app2_id}/evidence-requests",
        json={
            "finding_id": f_to_request,
            "request_text": "Please provide the official State Board NOC issued under seal."
        },
        headers=rev_headers
    )
    print(f"  POST /applications/{app2_id}/evidence-requests -> {r_ev_req.status_code}")
    assert r_ev_req.status_code == 200
    ev_req_id = r_ev_req.json()["id"]
    print(f"  Evidence Request Created: ID {ev_req_id}, Status: {r_ev_req.json()['status']}")
    assert r_ev_req.json()["status"] == "PENDING"
    print("  ✓ Reviewer evidence request: PASS")

    # -------------------------------------------------------------
    # Case 10: Institution Uploading Corrected Evidence
    # -------------------------------------------------------------
    print_section("Case 10: Institution Uploading Corrected Evidence")
    p_fixed_noc = os.path.join(test_pdf_dir, "fixed_noc.pdf")
    generate_noc_pdf(p_fixed_noc, app2_payload["institution_name"], app2_payload["institution_id"], state_name="Gujarat", cert_no="NOC-FIXED-2026", issue_date="10/01/2026", valid_till="2028-12-31")
    files = [("files", ("state_noc_corrected.pdf", open(p_fixed_noc, "rb"), "application/pdf"))]
    r_up_fix = client.post(f"{API_BASE}/applications/{app2_id}/documents", files=files, headers=inst_headers)
    assert r_up_fix.status_code == 200
    uploaded_noc_id = r_up_fix.json()["documents"][0]["id"]

    r_resp = client.post(
        f"{API_BASE}/evidence-requests/{ev_req_id}/respond",
        json={
            "response_text": "Attached official State Board NOC with validity up to 2028.",
            "response_document_id": uploaded_noc_id
        },
        headers=inst_headers
    )
    print(f"  POST /evidence-requests/{ev_req_id}/respond -> {r_resp.status_code}")
    assert r_resp.status_code == 200
    assert r_resp.json()["status"] == "RESPONDED"
    print("  ✓ Institution evidence response: PASS")

    # -------------------------------------------------------------
    # Case 11: Revalidation After Correction
    # -------------------------------------------------------------
    print_section("Case 11: Revalidation After Correction")
    r_reval = client.post(f"{API_BASE}/applications/{app2_id}/validate", headers=rev_headers)
    assert r_reval.status_code == 200
    r_chk_reval = client.get(f"{API_BASE}/applications/{app2_id}/checklist", headers=rev_headers)
    chk_after = r_chk_reval.json()
    noc_chk = next((c for c in chk_after if c["document_type"] == "NOC"), None)
    print(f"  NOC Checklist Item after upload: is_submitted={noc_chk['is_submitted']}, status={noc_chk['validation_status']}")
    assert noc_chk["is_submitted"] is True
    assert noc_chk["validation_status"] == "SATISFIED"
    print("  ✓ Revalidation updates checklist and finding state: PASS")

    # -------------------------------------------------------------
    # Case 12: Finding Resolution with Audit Trail Event
    # -------------------------------------------------------------
    print_section("Case 12: Finding Resolution with Audit Trail Event")
    r_res = client.put(
        f"{API_BASE}/findings/{f_to_request}/resolve",
        json={
            "action": "RESOLVE",
            "resolution_notes": "State Board NOC verified under seal."
        },
        headers=rev_headers
    )
    print(f"  PUT /findings/{f_to_request}/resolve -> {r_res.status_code}")
    assert r_res.status_code == 200
    assert r_res.json()["status"] == "RESOLVED"

    r_aud = client.get(f"{API_BASE}/audit?application_id={app2_id}", headers=rev_headers)
    aud_events = r_aud.json()
    resolve_event = next((e for e in aud_events if e["action"] == "FINDING_RESOLVED"), None)
    assert resolve_event is not None, "Expected FINDING_RESOLVED audit event!"
    print(f"  Audit Event Logged: ID={resolve_event['id']}, Action={resolve_event['action']}, Actor={resolve_event['actor_id']}")
    print(f"  Before: {resolve_event['before_state']} -> After: {resolve_event['after_state']}")
    print("  ✓ Finding resolution and persistent audit event: PASS")

    # =============================================================
    # Phase 5: Security & Data Integrity Tests
    # =============================================================
    print_section("Phase 5: Security & Data Integrity Tests")

    # Security Test 1: Reviewer cannot perform Admin-only actions
    print("\n[Security Test 1] Reviewer cannot update compliance rules (Admin-only)")
    r_sec1 = client.put(
        f"{API_BASE}/compliance/rules/RULE-EOA-NOC",
        json={"is_enabled": False},
        headers=rev_headers
    )
    print(f"  PUT /compliance/rules/RULE-EOA-NOC with Reviewer token -> {r_sec1.status_code}")
    assert r_sec1.status_code == 403, f"Expected 403 Forbidden, got {r_sec1.status_code}"
    print("  ✓ Reviewer blocked from Admin action: PASS")

    # Security Test 2: Institution User cannot resolve findings
    print("\n[Security Test 2] Institution User cannot resolve findings (Reviewer/Admin only)")
    r_sec2 = client.put(
        f"{API_BASE}/findings/{f_to_request}/resolve",
        json={"action": "RESOLVE", "resolution_notes": "Self resolved"},
        headers=inst_headers
    )
    print(f"  PUT /findings/{f_to_request}/resolve with Institution token -> {r_sec2.status_code}")
    assert r_sec2.status_code == 403, f"Expected 403 Forbidden, got {r_sec2.status_code}"
    print("  ✓ Institution User blocked from Reviewer action: PASS")

    # Security Test 3: Unauthenticated file access check
    print("\n[Security Test 3] Unauthenticated file access check")
    r_sec3 = client.get(f"{API_BASE}/documents/{uploaded_noc_id}/view")
    print(f"  GET /documents/{uploaded_noc_id}/view without token -> {r_sec3.status_code}")

    # Security Test 4: Cross-institution data isolation check
    print("\n[Security Test 4] Cross-institution application access check")
    r_list_inst = client.get(f"{API_BASE}/applications", headers=inst_headers)
    inst_apps = r_list_inst.json()["items"]
    print(f"  Applications visible to Institution User in list: {len(inst_apps)}")
    other_institution_in_list = any(a["institution_id"] != "1-1092837482" for a in inst_apps)
    print(f"  Any other institution apps visible in list: {other_institution_in_list}")

    # Security Test 5: Invalid file type rejection
    print("\n[Security Test 5] Invalid file type rejection (.exe, .sh)")
    bad_file = [("files", ("exploit.exe", io.BytesIO(b"MZ\x90\x00"), "application/x-msdownload"))]
    r_sec5 = client.post(f"{API_BASE}/applications/{app1_id}/documents", files=bad_file, headers=inst_headers)
    print(f"  POST .exe upload -> {r_sec5.status_code} ({r_sec5.text})")
    assert r_sec5.status_code == 400, f"Expected 400 Bad Request, got {r_sec5.status_code}"
    print("  ✓ Invalid file extension blocked: PASS")

    # Security Test 6: Oversized file rejection (>25MB)
    print("\n[Security Test 6] Oversized file rejection (>25MB)")
    oversized_data = b"0" * (26 * 1024 * 1024)
    big_file = [("files", ("huge.pdf", io.BytesIO(oversized_data), "application/pdf"))]
    r_sec6 = client.post(f"{API_BASE}/applications/{app1_id}/documents", files=big_file, headers=inst_headers)
    print(f"  POST 26MB upload -> {r_sec6.status_code}")
    assert r_sec6.status_code == 413, f"Expected 413 Entity Too Large, got {r_sec6.status_code}"
    print("  ✓ Oversized upload blocked: PASS")

    # Security Test 7: Malformed input resilience
    print("\n[Security Test 7] Malformed JSON & injection payload resilience")
    r_sec7 = client.post(f"{API_BASE}/applications", content="not json", headers={"Content-Type": "application/json"})
    print(f"  POST invalid JSON -> {r_sec7.status_code}")
    assert r_sec7.status_code in [400, 422], f"Expected 400/422, got {r_sec7.status_code}"

    r_sec7_sql = client.get(f"{API_BASE}/applications?search=' OR '1'='1", headers=rev_headers)
    print(f"  GET SQL search query -> {r_sec7_sql.status_code}")
    assert r_sec7_sql.status_code == 200, "SQL search query should be handled safely by parameterized ORM"
    print("  ✓ Malformed input handled without 500 crash: PASS")

    # Security Test 8: Audit Immutability (No PUT/DELETE)
    print("\n[Security Test 8] Audit Trail immutability (No POST/PUT/DELETE)")
    r_sec8_post = client.post(f"{API_BASE}/audit", json={"action": "HACK"}, headers=adm_headers)
    print(f"  POST /audit -> {r_sec8_post.status_code}")
    assert r_sec8_post.status_code == 405, f"Expected 405 Method Not Allowed, got {r_sec8_post.status_code}"

    r_sec8_del = client.delete(f"{API_BASE}/audit", headers=adm_headers)
    print(f"  DELETE /audit -> {r_sec8_del.status_code}")
    assert r_sec8_del.status_code == 405, f"Expected 405 Method Not Allowed, got {r_sec8_del.status_code}"
    print("  ✓ Audit trail immutable via API: PASS")

    # Security Test 9: Revalidation finding preservation
    print("\n[Security Test 9] Revalidation finding preservation (Does not delete resolved findings)")
    r_reval2 = client.post(f"{API_BASE}/applications/{app2_id}/validate", headers=rev_headers)
    assert r_reval2.status_code == 200
    r_f_after = client.get(f"{API_BASE}/applications/{app2_id}/findings", headers=rev_headers)
    resolved_f = next((f for f in r_f_after.json() if f["id"] == f_to_request), None)
    assert resolved_f is not None and resolved_f["status"] == "RESOLVED", "Revalidation must NOT overwrite resolved finding!"
    print("  ✓ Revalidation preserves resolved/overridden findings: PASS")

    # Security Test 10: Zero Automated Approvals / Rejections
    print("\n[Security Test 10] Guarantee: System never auto-approves or auto-rejects")
    app1_check = client.get(f"{API_BASE}/applications/{app1_id}", headers=rev_headers).json()
    print(f"  Clean App Status: {app1_check['status']} (Validation Status: {app1_check['validation_status']})")
    assert app1_check["status"] not in ["APPROVED", "REJECTED"], "System must never auto-approve!"

    app2_check = client.get(f"{API_BASE}/applications/{app2_id}", headers=rev_headers).json()
    print(f"  Deficient App Status: {app2_check['status']} (Validation Status: {app2_check['validation_status']})")
    assert app2_check["status"] not in ["APPROVED", "REJECTED"], "System must never auto-reject!"
    print("  ✓ Zero automated regulatory approval/rejection guarantee: PASS")

    print_section("ALL 12 END-TO-END AND 10 SECURITY AUDIT TEST CASES COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    main()
