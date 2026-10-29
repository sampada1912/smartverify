import io
import os
import uuid
import pytest
from fastapi.testclient import TestClient
import fitz
from PIL import Image
from app.main import app

client = TestClient(app)


def get_auth_token(username: str = "institution_demo", password: str = "password123") -> str:
    resp = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, f"Login failed for {username}: {resp.text}"
    return resp.json()["access_token"]


def create_sample_pdf_bytes(text: str = "All India Council for Technical Education Extension of Approval Letter") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_sample_png_bytes() -> bytes:
    img = Image.new("RGB", (120, 60), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def create_sample_csv_bytes() -> bytes:
    content = (
        "faculty_name,designation,qualification,department,date_of_joining\n"
        "Dr. Suresh Rao,Professor,Ph.D,Computer Science and Engineering,2018-07-01\n"
        "Dr. Anita Sharma,Associate Professor,Ph.D,Information Technology,2020-01-15\n"
        "Er. Rajesh Kumar,Assistant Professor,M.Tech,Computer Science,2021-08-20\n"
    )
    return content.encode("utf-8")


@pytest.fixture
def draft_application():
    token = get_auth_token("institution_demo")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "institution_id": "1-1092837482",
        "institution_name": "Delhi Institute of Technology & Management",
        "category": "EXTENSION_OF_APPROVAL",
        "academic_year": "2026-27",
        "programme": "ENGINEERING_AND_TECHNOLOGY",
        "course_name": "Computer Science and Engineering",
        "existing_intake": 120,
        "requested_intake": 120,
        "contact_person": "Dr. Upload Test Admin",
        "contact_email": "upload_test@ditm.edu.in",
        "contact_phone": "+91-9876543210"
    }
    resp = client.post("/api/v1/applications", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()


# 1. Successful PDF upload
def test_successful_pdf_upload(draft_application):
    token = get_auth_token("institution_demo")
    headers = {"Authorization": f"Bearer {token}"}
    app_id = draft_application["id"]

    pdf_bytes = create_sample_pdf_bytes("AICTE Approval Process Handbook Extension of Approval letter 2026-27")
    files = [
        ("files", ("aicte_eoa_letter.pdf", pdf_bytes, "application/pdf"))
    ]

    resp = client.post(f"/api/v1/applications/{app_id}/documents", files=files, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["documents"]) == 1
    doc = data["documents"][0]
    assert doc["original_filename"] == "aicte_eoa_letter.pdf"
    assert doc["mime_type"] == "application/pdf"
    assert doc["doc_type"] == "PREVIOUS_APPROVAL"
    assert doc["ocr_status"] == "COMPLETED"
    assert len(doc["sha256_hash"]) == 64


# 2. Successful image upload (PNG)
def test_successful_image_upload(draft_application):
    token = get_auth_token("institution_demo")
    headers = {"Authorization": f"Bearer {token}"}
    app_id = draft_application["id"]

    png_bytes = create_sample_png_bytes()
    files = [
        ("files", ("campus_infrastructure_photo.png", png_bytes, "image/png"))
    ]

    resp = client.post(f"/api/v1/applications/{app_id}/documents", files=files, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["documents"]) == 1
    doc = data["documents"][0]
    assert doc["original_filename"] == "campus_infrastructure_photo.png"
    assert doc["mime_type"] == "image/png"


# 3. Successful CSV upload
def test_successful_csv_upload(draft_application):
    token = get_auth_token("institution_demo")
    headers = {"Authorization": f"Bearer {token}"}
    app_id = draft_application["id"]

    csv_bytes = create_sample_csv_bytes()
    files = [
        ("files", ("teaching_faculty_list.csv", csv_bytes, "text/csv"))
    ]

    resp = client.post(f"/api/v1/applications/{app_id}/documents", files=files, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["documents"]) == 1
    doc = data["documents"][0]
    assert doc["original_filename"] == "teaching_faculty_list.csv"
    assert doc["doc_type"] == "FACULTY_LIST"
    assert "Structured CSV Data" in (doc["extracted_text_preview"] or "")


# 4. Multi-file upload in single request with custom doc_types
def test_multi_file_upload(draft_application):
    token = get_auth_token("institution_demo")
    headers = {"Authorization": f"Bearer {token}"}
    app_id = draft_application["id"]

    pdf_bytes = create_sample_pdf_bytes("Format-1 Statutory Affidavit Non-Judicial Stamp")
    csv_bytes = create_sample_csv_bytes()

    files = [
        ("files", ("affidavit_format1.pdf", pdf_bytes, "application/pdf")),
        ("files", ("faculty_roster.csv", csv_bytes, "text/csv"))
    ]
    # Pass doc_type as form parameter
    data = {"doc_types": ["AFFIDAVIT", "FACULTY_LIST"]}

    resp = client.post(
        f"/api/v1/applications/{app_id}/documents",
        files=files,
        data=data,
        headers=headers
    )
    if resp.status_code != 200:
        print("UPLOAD ERROR:", resp.status_code, resp.text)
    assert resp.status_code == 200
    res_data = resp.json()
    assert len(res_data["documents"]) == 2
    types = [d["doc_type"] for d in res_data["documents"]]
    assert "AFFIDAVIT" in types
    assert "FACULTY_LIST" in types


# 5. Unsupported file rejection (e.g. .exe or .txt)
def test_unsupported_file_rejection(draft_application):
    token = get_auth_token("institution_demo")
    headers = {"Authorization": f"Bearer {token}"}
    app_id = draft_application["id"]

    files = [
        ("files", ("script.sh", b"#!/bin/bash\necho hello", "text/x-shellscript"))
    ]
    resp = client.post(f"/api/v1/applications/{app_id}/documents", files=files, headers=headers)
    assert resp.status_code == 400
    assert "Unsupported file extension" in resp.json()["detail"]


# 6. Oversized file rejection (> 25MB)
def test_oversized_file_rejection(draft_application):
    token = get_auth_token("institution_demo")
    headers = {"Authorization": f"Bearer {token}"}
    app_id = draft_application["id"]

    # 26 MB of dummy data
    oversized_bytes = b"0" * (26 * 1024 * 1024)
    files = [
        ("files", ("large_scan.pdf", oversized_bytes, "application/pdf"))
    ]
    resp = client.post(f"/api/v1/applications/{app_id}/documents", files=files, headers=headers)
    assert resp.status_code == 413
    assert "exceeds maximum allowed size" in resp.json()["detail"]


# 7. Unauthorized upload rejection
def test_unauthorized_upload_rejection(draft_application):
    app_id = draft_application["id"]

    # Unauthenticated request (no token)
    files = [("files", ("test.pdf", create_sample_pdf_bytes(), "application/pdf"))]
    resp = client.post(f"/api/v1/applications/{app_id}/documents", files=files)
    assert resp.status_code in (401, 403)

    # Cross-institution user request: register a different institution user
    token_admin = get_auth_token("admin_demo")
    headers_admin = {"Authorization": f"Bearer {token_admin}"}
    unique_user = f"other_inst_{uuid.uuid4().hex[:6]}"
    client.post(
        "/api/v1/auth/users",
        json={
            "username": unique_user,
            "email": f"{unique_user}@example.com",
            "password": "password123",
            "full_name": "Other Institution",
            "role": "INSTITUTION",
            "institution_id": "9-9999999999"
        },
        headers=headers_admin
    )

    other_token = get_auth_token(unique_user, "password123")
    other_headers = {"Authorization": f"Bearer {other_token}"}

    resp = client.post(f"/api/v1/applications/{app_id}/documents", files=files, headers=other_headers)
    assert resp.status_code == 403
    assert "Cross-institution" in resp.json()["detail"]


# 8. Document Deletion & Checklist Unlinking
def test_document_deletion_and_checklist_unlinking(draft_application):
    token = get_auth_token("institution_demo")
    headers = {"Authorization": f"Bearer {token}"}
    app_id = draft_application["id"]

    # Upload affidavit
    pdf_bytes = create_sample_pdf_bytes("Format-1 Statutory Affidavit Non-Judicial Stamp")
    files = [("files", ("statutory_affidavit.pdf", pdf_bytes, "application/pdf"))]
    upload_resp = client.post(
        f"/api/v1/applications/{app_id}/documents",
        files=files,
        data={"doc_type": "AFFIDAVIT"},
        headers=headers
    )
    assert upload_resp.status_code == 200
    doc_id = upload_resp.json()["documents"][0]["id"]

    # Verify checklist item is SATISFIED
    chk_resp = client.get(f"/api/v1/applications/{app_id}/checklist", headers=headers)
    affidavit_chk = [i for i in chk_resp.json() if i["document_type"] == "AFFIDAVIT"][0]
    assert affidavit_chk["is_submitted"] is True
    assert affidavit_chk["document_id"] == doc_id
    assert affidavit_chk["validation_status"] == "SATISFIED"

    # Delete the document
    del_resp = client.delete(f"/api/v1/documents/{doc_id}", headers=headers)
    assert del_resp.status_code == 200
    assert "deleted successfully" in del_resp.json()["message"]

    # Verify checklist item reverted to MISSING
    chk_resp_after = client.get(f"/api/v1/applications/{app_id}/checklist", headers=headers)
    affidavit_chk_after = [i for i in chk_resp_after.json() if i["document_type"] == "AFFIDAVIT"][0]
    assert affidavit_chk_after["is_submitted"] is False
    assert affidavit_chk_after["document_id"] is None
    assert affidavit_chk_after["validation_status"] == "MISSING"


# 9. Document Reclassification (PATCH /documents/{doc_id}/type)
def test_document_reclassification(draft_application):
    token = get_auth_token("institution_demo")
    headers = {"Authorization": f"Bearer {token}"}
    app_id = draft_application["id"]

    pdf_bytes = create_sample_pdf_bytes("Generic government document")
    files = [("files", ("generic_document.pdf", pdf_bytes, "application/pdf"))]
    upload_resp = client.post(f"/api/v1/applications/{app_id}/documents", files=files, headers=headers)
    doc_id = upload_resp.json()["documents"][0]["id"]

    # Reclassify to NOC
    patch_resp = client.patch(
        f"/api/v1/documents/{doc_id}/type",
        json={"doc_type": "NOC"},
        headers=headers
    )
    assert patch_resp.status_code == 200
    updated_doc = patch_resp.json()
    assert updated_doc["doc_type"] == "NOC"
    assert updated_doc["classification_method"] == "MANUAL_USER_OVERRIDE"


# 10. Draft saving with incomplete documents and submission workflow
def test_draft_saving_and_submission_pipeline():
    token = get_auth_token("institution_demo")
    headers = {"Authorization": f"Bearer {token}"}

    # Create draft
    payload = {
        "institution_id": "1-1092837482",
        "institution_name": "Delhi Institute of Technology & Management",
        "category": "EXTENSION_OF_APPROVAL",
        "academic_year": "2026-27",
        "programme": "ENGINEERING_AND_TECHNOLOGY",
        "course_name": "Electrical and Electronics Engineering",
        "existing_intake": 60,
        "requested_intake": 60,
        "contact_person": "Dr. Pipeline Lead",
        "contact_email": "pipeline@ditm.edu.in",
        "contact_phone": "+91-9123456789"
    }
    create_resp = client.post("/api/v1/applications", json=payload, headers=headers)
    assert create_resp.status_code == 201
    app_id = create_resp.json()["id"]

    # Attach only 1 document (incomplete checklist)
    pdf_bytes = create_sample_pdf_bytes("Previous year approval letter")
    files = [("files", ("eoa_2025.pdf", pdf_bytes, "application/pdf"))]
    client.post(f"/api/v1/applications/{app_id}/documents", files=files, headers=headers)

    # Incomplete draft remains in DRAFT status
    app_resp = client.get(f"/api/v1/applications/{app_id}", headers=headers)
    assert app_resp.json()["status"] == "DRAFT"

    # Now submit for scrutiny
    submit_resp = client.post(f"/api/v1/applications/{app_id}/submit", headers=headers)
    assert submit_resp.status_code == 200
    submitted = submit_resp.json()
    assert submitted["status"] == "SUBMITTED"
    assert submitted["submission_date"] is not None

    # Check that validation was executed and findings exist
    findings_resp = client.get(f"/api/v1/applications/{app_id}/findings", headers=headers)
    assert findings_resp.status_code == 200
