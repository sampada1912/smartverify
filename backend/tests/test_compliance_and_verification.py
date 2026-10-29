import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_compliance_evaluations():
    login = client.post("/api/v1/auth/login", json={"username": "reviewer_demo", "password": "password123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Clean app 1 should have PASS compliance evaluations
    resp = client.get("/api/v1/applications/APP-2026-0001/compliance", headers=headers)
    assert resp.status_code == 200
    evals = resp.json()
    assert len(evals) >= 5
    assert any(e["status"] == "PASS" for e in evals)


def test_simulated_verification_adapter():
    login = client.post("/api/v1/auth/login", json={"username": "reviewer_demo", "password": "password123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Successful verification on active certificate
    req_success = {
        "certificate_number": "NOC-2025-99882",
        "authority_name": "STATE_TECHNICAL_BOARD_MOCK"
    }
    resp1 = client.post("/api/v1/applications/APP-2026-0001/verify", json=req_success, headers=headers)
    assert resp1.status_code == 200
    res1 = resp1.json()
    assert res1["status"] == "VERIFIED"
    assert res1["is_simulated"] is True

    # 2. Expired certificate detection
    req_exp = {
        "certificate_number": "NOC-MP-2023-EXPIRED",
        "authority_name": "STATE_TECHNICAL_BOARD_MOCK"
    }
    resp2 = client.post("/api/v1/applications/APP-2026-0003/verify", json=req_exp, headers=headers)
    assert resp2.status_code == 200
    res2 = resp2.json()
    assert res2["status"] == "EXPIRED"
    assert res2["is_simulated"] is True

    # 3. Mismatch detection (institution ID mismatch in authority register)
    req_mismatch = {
        "certificate_number": "NOC-TEL-2025-MISMATCH",
        "authority_name": "STATE_TECHNICAL_BOARD_MOCK"
    }
    resp3 = client.post("/api/v1/applications/APP-2026-0007/verify", json=req_mismatch, headers=headers)
    assert resp3.status_code == 200
    res3 = resp3.json()
    assert res3["status"] == "MISMATCH_DETECTED"
    assert res3["is_simulated"] is True
    assert "Institution ID mismatch" in res3["mismatch_details"]


def test_admin_can_toggle_compliance_rules():
    login = client.post("/api/v1/auth/login", json={"username": "admin_demo", "password": "password123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get rules
    rules_resp = client.get("/api/v1/compliance/rules", headers=headers)
    assert rules_resp.status_code == 200
    rules = rules_resp.json()
    target_rule = rules[0]
    rule_id = target_rule["rule_id"]

    # Toggle rule
    update_resp = client.put(
        f"/api/v1/compliance/rules/{rule_id}",
        json={"is_enabled": False},
        headers=headers
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["is_enabled"] is False

    # Restore rule
    restore_resp = client.put(
        f"/api/v1/compliance/rules/{rule_id}",
        json={"is_enabled": True},
        headers=headers
    )
    assert restore_resp.status_code == 200
    assert restore_resp.json()["is_enabled"] is True
