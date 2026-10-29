import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_audit_trail_logging_and_filtering():
    login = client.post("/api/v1/auth/login", json={"username": "admin_demo", "password": "password123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch audit events
    resp = client.get("/api/v1/audit", headers=headers)
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) >= 1

    # Filter by application_id
    resp_filtered = client.get("/api/v1/audit?application_id=APP-2026-0001", headers=headers)
    assert resp_filtered.status_code == 200
    app1_events = resp_filtered.json()
    for ev in app1_events:
        assert ev["application_id"] == "APP-2026-0001"


def test_dashboard_metrics():
    login = client.post("/api/v1/auth/login", json={"username": "reviewer_demo", "password": "password123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/dashboard/stats", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_applications"] >= 8
    assert data["open_findings_count"] >= 1
    assert data["missing_documents_count"] >= 1
    assert data["expired_documents_count"] >= 1
    assert "recent_activity" in data
    assert "recent_applications" in data
