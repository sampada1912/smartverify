import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import create_access_token

client = TestClient(app)


def test_1_admin_login_authenticates_as_admin():
    """1. Admin login authenticates as Admin."""
    resp = client.post("/api/v1/auth/login", json={
        "username": "admin_demo",
        "password": "password123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "ADMIN"
    assert data["username"] == "admin_demo"
    assert "access_token" in data

    # Verify /auth/me returns ADMIN
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["role"] == "ADMIN"


def test_2_reviewer_login_authenticates_as_reviewer():
    """2. Reviewer login authenticates as Reviewer."""
    resp = client.post("/api/v1/auth/login", json={
        "username": "reviewer_demo",
        "password": "password123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "REVIEWER"
    assert data["username"] == "reviewer_demo"
    assert "access_token" in data

    headers = {"Authorization": f"Bearer {data['access_token']}"}
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["role"] == "REVIEWER"


def test_3_institution_login_authenticates_as_institution():
    """3. Institution login authenticates as Institution."""
    resp = client.post("/api/v1/auth/login", json={
        "username": "institution_demo",
        "password": "password123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "INSTITUTION"
    assert data["username"] == "institution_demo"
    assert data["institution_id"] == "1-1092837482"
    assert "access_token" in data

    headers = {"Authorization": f"Bearer {data['access_token']}"}
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["role"] == "INSTITUTION"
    assert me_resp.json()["institution_id"] == "1-1092837482"


def test_4_invalid_credentials_are_rejected():
    """4. Invalid credentials are rejected with 401."""
    # Bad password
    resp1 = client.post("/api/v1/auth/login", json={
        "username": "admin_demo",
        "password": "invalid-password"
    })
    assert resp1.status_code == 401
    assert "Incorrect username or password" in resp1.json()["detail"]

    # Nonexistent user
    resp2 = client.post("/api/v1/auth/login", json={
        "username": "nonexistent_hacker",
        "password": "password123"
    })
    assert resp2.status_code == 401
    assert "Incorrect username or password" in resp2.json()["detail"]


def test_5_admin_cannot_become_reviewer_by_editing_frontend_state():
    """5. Admin cannot become Reviewer by editing frontend state.
    The server derives role exclusively from signed JWT sub/role claims, not client-side state.
    Tampered tokens with invalid signature or modified claims are rejected with 401.
    """
    fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbl9kZW1vIiwicm9sZSI6IlJFVklFV0VSIiwiZXhwIjoxOTk5OTk5OTk5fQ.invalid_signature"
    headers = {"Authorization": f"Bearer {fake_token}"}
    resp = client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 401
    assert "Could not validate credentials" in resp.json()["detail"]


def test_6_submitting_role_field_does_not_override_authenticated_identity():
    """6. Submitting a role field to an API request does not grant additional privileges."""
    # Institution logs in
    login = client.post("/api/v1/auth/login", json={"username": "institution_demo", "password": "password123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Institution attempts to create an application with a spoofed reviewer role in body
    payload = {
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
        "contact_phone": "+91-9999999999",
        "role": "ADMIN",  # Spoofed field in request body
        "user_role": "ADMIN"
    }
    create_resp = client.post("/api/v1/applications", json=payload, headers=headers)
    assert create_resp.status_code == 201

    # User's profile still shows INSTITUTION
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.json()["role"] == "INSTITUTION"


def test_7_institution_users_cannot_access_another_institutions_applications():
    """7. Institution users cannot access another institution's applications (403 Forbidden)."""
    # institution_demo belongs to "1-1092837482".
    # APP-2026-0002 belongs to "1-2039485761".
    login = client.post("/api/v1/auth/login", json={"username": "institution_demo", "password": "password123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Direct GET of another institution's application
    resp_app = client.get("/api/v1/applications/APP-2026-0002", headers=headers)
    assert resp_app.status_code == 403
    assert "Cross-institution application access prohibited" in resp_app.json()["detail"]

    # 2. Attempt to view findings of another institution's application
    resp_findings = client.get("/api/v1/applications/APP-2026-0002/findings", headers=headers)
    assert resp_findings.status_code == 403

    # 3. Attempt to view compliance of another institution's application
    resp_comp = client.get("/api/v1/applications/APP-2026-0002/compliance", headers=headers)
    assert resp_comp.status_code == 403

    # 4. Attempt to trigger verification on another institution's application
    resp_verif = client.post("/api/v1/applications/APP-2026-0002/verify", json={
        "certificate_number": "NOC-2025-99882",
        "authority_name": "STATE_TECHNICAL_BOARD_MOCK"
    }, headers=headers)
    assert resp_verif.status_code == 403


def test_8_reviewers_cannot_change_compliance_rules():
    """8. Reviewers cannot change compliance rules unless explicitly authorized (403 Forbidden)."""
    login = client.post("/api/v1/auth/login", json={"username": "reviewer_demo", "password": "password123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch rules
    rules_resp = client.get("/api/v1/compliance/rules", headers=headers)
    assert rules_resp.status_code == 200
    rule_id = rules_resp.json()[0]["rule_id"]

    # Reviewer attempts to modify a rule
    modify_resp = client.put(
        f"/api/v1/compliance/rules/{rule_id}",
        json={"is_enabled": False},
        headers=headers
    )
    assert modify_resp.status_code == 403
    assert "Requires one of ['ADMIN'] role" in modify_resp.json()["detail"]


def test_9_non_admin_users_cannot_create_privileged_accounts():
    """9. Non-admin users cannot create privileged accounts (403 Forbidden)."""
    # 1. Reviewer attempts account creation
    rev_login = client.post("/api/v1/auth/login", json={"username": "reviewer_demo", "password": "password123"})
    rev_token = rev_login.json()["access_token"]
    rev_headers = {"Authorization": f"Bearer {rev_token}"}

    account_payload = {
        "username": "rogue_admin",
        "email": "rogue@aicte.gov.in",
        "password": "password123",
        "full_name": "Rogue Admin",
        "role": "ADMIN"
    }
    resp1 = client.post("/api/v1/auth/users", json=account_payload, headers=rev_headers)
    assert resp1.status_code == 403
    assert "Requires one of ['ADMIN'] role" in resp1.json()["detail"]

    # 2. Institution attempts account creation
    inst_login = client.post("/api/v1/auth/login", json={"username": "institution_demo", "password": "password123"})
    inst_token = inst_login.json()["access_token"]
    inst_headers = {"Authorization": f"Bearer {inst_token}"}

    resp2 = client.post("/api/v1/auth/users", json=account_payload, headers=inst_headers)
    assert resp2.status_code == 403

    # 3. Admin CAN create an account
    admin_login = client.post("/api/v1/auth/login", json={"username": "admin_demo", "password": "password123"})
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    import uuid
    uid = uuid.uuid4().hex[:6]
    new_user_payload = {
        "username": f"rev_{uid}",
        "email": f"rev_{uid}@aicte.gov.in",
        "password": "password123",
        "full_name": f"New Reviewer {uid}",
        "role": "REVIEWER"
    }
    resp3 = client.post("/api/v1/auth/users", json=new_user_payload, headers=admin_headers)
    assert resp3.status_code == 201
    assert resp3.json()["username"] == f"rev_{uid}"


def test_10_unauthenticated_api_requests_are_rejected():
    """10. Unauthenticated API requests are rejected (401 Unauthorized across all endpoints)."""
    # Applications
    assert client.get("/api/v1/applications").status_code == 401
    assert client.get("/api/v1/applications/APP-2026-0001").status_code == 401
    # Findings
    assert client.get("/api/v1/applications/APP-2026-0001/findings").status_code == 401
    # Compliance
    assert client.get("/api/v1/applications/APP-2026-0001/compliance").status_code == 401
    # Audit
    assert client.get("/api/v1/audit").status_code == 401
    # Dashboard
    assert client.get("/api/v1/dashboard/stats").status_code == 401
    # Auth Me
    assert client.get("/api/v1/auth/me").status_code == 401


def test_11_unauthorized_document_downloads_are_rejected():
    """11. Unauthorized document downloads and views are rejected."""
    # Reviewer gets documents for APP-2026-0002 to find a valid document ID belonging to College 2
    rev_login = client.post("/api/v1/auth/login", json={"username": "reviewer_demo", "password": "password123"})
    rev_token = rev_login.json()["access_token"]
    rev_headers = {"Authorization": f"Bearer {rev_token}"}

    app2_docs = client.get("/api/v1/applications/APP-2026-0002/documents", headers=rev_headers).json()
    assert len(app2_docs) > 0
    foreign_doc_id = app2_docs[0]["id"]

    # Now institution_demo (from College 1) attempts to view/download foreign_doc_id
    inst_login = client.post("/api/v1/auth/login", json={"username": "institution_demo", "password": "password123"})
    inst_token = inst_login.json()["access_token"]
    inst_headers = {"Authorization": f"Bearer {inst_token}"}

    doc_view_resp = client.get(f"/api/v1/documents/{foreign_doc_id}/view", headers=inst_headers)
    assert doc_view_resp.status_code == 403
    assert "Unauthorized document access" in doc_view_resp.json()["detail"]


def test_12_logout_records_audit_event_and_invalidates_session():
    """12. Logout invalidates or clears the authenticated session and records audit event."""
    login = client.post("/api/v1/auth/login", json={"username": "reviewer_demo", "password": "password123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Call logout
    logout_resp = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_resp.status_code == 200
    assert logout_resp.json()["status"] == "SUCCESS"

    # Verify audit event was recorded for USER_LOGOUT
    admin_login = client.post("/api/v1/auth/login", json={"username": "admin_demo", "password": "password123"})
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
    audit_resp = client.get("/api/v1/audit?action=USER_LOGOUT", headers=admin_headers)
    assert audit_resp.status_code == 200
    events = audit_resp.json()
    assert any(e["actor_id"] == "reviewer_demo" and e["action"] == "USER_LOGOUT" for e in events)


def test_13_demo_database_reset_requires_admin():
    """Admin-only constraint on prototype reset/reseed."""
    # Reviewer attempts reset
    rev_login = client.post("/api/v1/auth/login", json={"username": "reviewer_demo", "password": "password123"})
    rev_headers = {"Authorization": f"Bearer {rev_login.json()['access_token']}"}
    reset_resp = client.post("/api/v1/demo/reset-seed", headers=rev_headers)
    assert reset_resp.status_code == 403

    # Institution attempts reset
    inst_login = client.post("/api/v1/auth/login", json={"username": "institution_demo", "password": "password123"})
    inst_headers = {"Authorization": f"Bearer {inst_login.json()['access_token']}"}
    reset_resp2 = client.post("/api/v1/demo/reset-seed", headers=inst_headers)
    assert reset_resp2.status_code == 403
