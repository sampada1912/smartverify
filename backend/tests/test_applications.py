import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_applications():
    # Login as reviewer
    login = client.post("/api/v1/auth/login", json={"username": "reviewer_demo", "password": "password123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/applications", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 8
    assert len(data["items"]) >= 8


def test_create_and_submit_application():
    login = client.post("/api/v1/auth/login", json={"username": "institution_demo", "password": "password123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Draft Application
    create_payload = {
        "institution_id": "1-1092837482",
        "institution_name": "Delhi Institute of Technology & Management",
        "category": "EXTENSION_OF_APPROVAL",
        "academic_year": "2026-27",
        "programme": "ENGINEERING_AND_TECHNOLOGY",
        "course_name": "Computer Science and Engineering",
        "existing_intake": 120,
        "requested_intake": 120,
        "contact_person": "Dr. Testing Officer",
        "contact_email": "test@college.edu",
        "contact_phone": "+91-9999999999"
    }
    create_resp = client.post("/api/v1/applications", json=create_payload, headers=headers)
    assert create_resp.status_code == 201
    created_app = create_resp.json()
    app_id = created_app["id"]
    assert created_app["status"] == "DRAFT"

    # 2. Check initialized checklist
    chk_resp = client.get(f"/api/v1/applications/{app_id}/checklist", headers=headers)
    assert chk_resp.status_code == 200
    chk_items = chk_resp.json()
    assert len(chk_items) >= 5 # Applicable items for EXTENSION_OF_APPROVAL

    # 3. Submit Application
    submit_resp = client.post(f"/api/v1/applications/{app_id}/submit", headers=headers)
    assert submit_resp.status_code == 200
    submitted_data = submit_resp.json()
    assert submitted_data["status"] == "SUBMITTED"
    assert submitted_data["submission_date"] is not None
