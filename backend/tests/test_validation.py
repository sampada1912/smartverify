import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_clean_application_has_no_deficiencies():
    # Scenario 1: Clean Application (APP-2026-0001)
    login = client.post("/api/v1/auth/login", json={"username": "reviewer_demo", "password": "password123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/applications/APP-2026-0001", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["validation_status"] == "CLEAN"
    assert data["high_findings_count"] == 0


def test_missing_document_finding():
    # Scenario 2: Missing Required Document (APP-2026-0002)
    login = client.post("/api/v1/auth/login", json={"username": "reviewer_demo", "password": "password123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/applications/APP-2026-0002/findings", headers=headers)
    assert resp.status_code == 200
    findings = resp.json()
    missing_findings = [f for f in findings if f["category"] == "MISSING_DOCUMENT"]
    assert len(missing_findings) >= 1
    assert any("Faculty Details" in f["title"] or "NOC" in f["title"] for f in missing_findings)


def test_expired_document_finding():
    # Scenario 3: Expired Document (APP-2026-0003)
    login = client.post("/api/v1/auth/login", json={"username": "reviewer_demo", "password": "password123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/applications/APP-2026-0003/findings", headers=headers)
    assert resp.status_code == 200
    findings = resp.json()
    expired = [f for f in findings if f["category"] == "EXPIRED_DOCUMENT"]
    assert len(expired) >= 1
    assert "Expired" in expired[0]["title"]


def test_duplicate_document_finding():
    # Scenario 6: Duplicate Document Detection (APP-2026-0006)
    login = client.post("/api/v1/auth/login", json={"username": "reviewer_demo", "password": "password123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/applications/APP-2026-0006/findings", headers=headers)
    assert resp.status_code == 200
    findings = resp.json()
    dups = [f for f in findings if f["category"] == "DUPLICATE_DOCUMENT"]
    assert len(dups) >= 1
    assert "Duplicate" in dups[0]["title"]


def test_reviewer_can_resolve_and_override_finding():
    login = client.post("/api/v1/auth/login", json={"username": "reviewer_demo", "password": "password123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch findings for app 2
    resp = client.get("/api/v1/applications/APP-2026-0002/findings", headers=headers)
    findings = resp.json()
    assert len(findings) > 0
    target_finding = findings[0]
    finding_id = target_finding["id"]

    # 1. Resolve finding
    resolve_resp = client.put(
        f"/api/v1/findings/{finding_id}/resolve",
        json={"action": "RESOLVE", "resolution_notes": "Document verified through alternative offline state gazette."},
        headers=headers
    )
    assert resolve_resp.status_code == 200
    resolved = resolve_resp.json()
    assert resolved["status"] == "RESOLVED"
    assert resolved["resolved_by"] == "reviewer_demo"

    # 2. Override finding status with mandatory reason
    override_resp = client.put(
        f"/api/v1/findings/{finding_id}/override",
        json={"new_status": "ESCALATED", "override_reason": "Escalated to Regional Hearing Committee for scrutiny."},
        headers=headers
    )
    assert override_resp.status_code == 200
    overridden = override_resp.json()
    assert overridden["status"] == "ESCALATED"
    assert overridden["override_reason"] == "Escalated to Regional Hearing Committee for scrutiny."
