import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app
from database import Base, engine, SessionLocal
from sqlalchemy.orm import Session

@pytest.fixture(scope="module")
def test_client():
    Base.metadata.create_all(bind=engine) 
    client = TestClient(app)
    yield client
    Base.metadata.drop_all(bind=engine) 

@pytest.fixture(scope="function")
def db_session():
    session: Session = SessionLocal()
    yield session
    session.rollback()
    session.close()

sample_customer = {
  "id": "string",
  "customer_name": "string",
  "email": "customer1@yopmail.com",
  "password": "password123",
  "confirmPassword": "password123",
  "phone": "string",
  "address": "string",
  "created_at": "2025-12-03T18:57:11.693Z",
  "is_active": "string"
}

login_data = {
    "email": "customer1@yopmail.com",
    "password": "password123"
}

# --- Tests ---

def test_signup_success(test_client):
    response = test_client.post("/signup", json=sample_customer)
    assert response.status_code == 200
    assert response.json()["message"] == "✅ Sign up successfully"

def test_signup_duplicate(test_client):
    response = test_client.post("/signup", json=sample_customer)
    assert response.status_code == 400
    assert response.json()["detail"] == "Customer already exists!"

def test_login_success(test_client):
    response = test_client.post("/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["message"] == "✅ Login successful"

def test_login_wrong_password(test_client):
    response = test_client.post("/login", json={"email": login_data["email"], "password": "wrongpass"})
    assert response.status_code == 401 or response.status_code == 404
    assert "Incorrect email or password" in response.json()["detail"]

def test_get_customers(test_client):
    response = test_client.get("/customers")
    assert response.status_code == 200
    data = response.json()
    assert "search_result" in data
    assert isinstance(data["search_result"], list)
    assert "next_cursor" in data
    assert "total_employee" in data

def test_get_customer_detail(test_client):
    customers_resp = test_client.get("/customers")
    customer_id = customers_resp.json()["search_result"][0]["id"]

    response = test_client.get(f"/customers/{customer_id}")
    assert response.status_code == 200
    customer = response.json()
    assert customer["id"] == customer_id
    assert customer["email"] == sample_customer["email"]

def test_delete_customer(test_client):
    customers_resp = test_client.get("/customers")
    customer_id = customers_resp.json()["search_result"][0]["id"]

    response = test_client.delete(f"/customers/{customer_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Customer deleted successfully"

    # Confirm deleted
    response = test_client.get(f"/customers/{customer_id}")
    assert response.status_code == 404
