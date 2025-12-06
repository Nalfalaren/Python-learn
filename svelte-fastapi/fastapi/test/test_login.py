import pytest
from fastapi.testclient import TestClient
import sys, os
from jose import jwt
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app
from database import Base, engine


@pytest.fixture(scope="module")
def test_client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    yield client
    Base.metadata.drop_all(bind=engine)


# ---------- SAMPLE DATA ----------
signup_data = {
    "email": "employee@test.com",
    "employee_name": "Test Employee",
    "password": "password123",
    "confirmPassword": "password123",
    "role": "EMPLOYEE"
}

login_data = {
    "email": "employee@test.com",
    "password": "password123",
}


# ---------- SIGNUP TESTS ----------

def test_signup_success(test_client):
    res = test_client.post("/auth/signup", json=signup_data)
    assert res.status_code == 200
    assert res.json()["message"] == "✅ Sign up successfully"


def test_signup_duplicate(test_client):
    res = test_client.post("/auth/signup", json=signup_data)
    assert res.status_code == 400
    # Bạn đang dùng detail chung "Incorrect email or password!" -> test theo đó
    assert res.json()["detail"] == "Account is existed!"


# ---------- LOGIN TESTS ----------

def test_login_success(test_client):
    res = test_client.post("/auth/login", json=login_data)
    assert res.status_code == 200

    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["message"] == "✅ Login successful"


def test_login_wrong_password(test_client):
    res = test_client.post("/auth/login", json={
        "email": login_data["email"],
        "password": "wrongpass"
    })
    assert res.status_code in (401, 404)
    assert "Incorrect email or password" in res.json()["detail"]


def test_login_unknown_email(test_client):
    res = test_client.post("/auth/login", json={
        "email": "abc@notfound.com",
        "password": "xxx"
    })
    assert res.status_code == 404
    assert "Incorrect email or password" in res.json()["detail"]


# ---------- REFRESH TOKEN TEST ----------

def test_refresh_token_success(test_client):
    login_res = test_client.post("/auth/login", json=login_data)
    refresh_token = login_res.json()["refresh_token"]

    res = test_client.post(
        "/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_refresh_token_missing_header(test_client):
    res = test_client.post("/auth/refresh")
    assert res.status_code == 401
    assert res.json()["message"] == "Missing refresh token"


def test_refresh_token_invalid(test_client):
    res = test_client.post(
        "/auth/refresh",
        headers={"Authorization": "Bearer INVALIDTOKEN"}
    )
    assert res.status_code == 401
    assert res.json()["message"] == "Invalid refresh token"


def test_logout_success(test_client):
    login_res = test_client.post("/auth/login", json=login_data)
    access_token = login_res.json()["access_token"]

    payload = jwt.decode(
        access_token,
        os.getenv("JWT_SECRET_KEY"),
        algorithms=[os.getenv("ALGORITHM")]
    )
    user_email = payload["sub"]

    res = test_client.post(
        "/auth/logout",
        json={"id": login_res.json().get("role")}, 
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert res.status_code in (200, 404)
