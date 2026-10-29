import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "SmartVerify" in data["system"]


def test_login_institution():
    response = client.post("/api/v1/auth/login", json={"username": "institution_demo", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "INSTITUTION"
    assert data["username"] == "institution_demo"
    assert data["institution_id"] == "1-1092837482"


def test_login_reviewer():
    response = client.post("/api/v1/auth/login", json={"username": "reviewer_demo", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "REVIEWER"
    assert data["username"] == "reviewer_demo"


def test_login_admin():
    response = client.post("/api/v1/auth/login", json={"username": "admin_demo", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "ADMIN"
    assert data["username"] == "admin_demo"


def test_login_invalid_password():
    response = client.post("/api/v1/auth/login", json={"username": "admin_demo", "password": "wrongpassword"})
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_me_endpoint():
    login_resp = client.post("/api/v1/auth/login", json={"username": "reviewer_demo", "password": "password123"})
    token = login_resp.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    data = me_resp.json()
    assert data["username"] == "reviewer_demo"
    assert data["role"] == "REVIEWER"
