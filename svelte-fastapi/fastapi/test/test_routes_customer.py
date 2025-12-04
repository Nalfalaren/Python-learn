import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta
from main import app
from database import Base, engine, SessionLocal
from apis.customer.models import CustomerBase
from apis.forget_password.models import PasswordResetTokenCustomerBase
from apis.forget_password.utils import hash_password
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# --- Fixtures ---
@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    session: Session = SessionLocal()
    yield session
    session.rollback()
    session.close()


# --- Seed helper ---
def seed_customer(session: Session, email="test@example.com"):
    customer = CustomerBase(
        id=str(uuid.uuid4()),
        email=email,
        customer_name="Test User",
        password=hash_password("password123"),
        phone="1234567890",
        address="123 Test St",
        created_at=datetime.utcnow(),
        is_active="Active",
        role="CUSTOMER"
    )
    session.add(customer)
    session.commit()
    return customer


def seed_reset_token(session: Session, customer_id: str, token="token123", expired=False):
    expires_at = datetime.utcnow() - timedelta(hours=1) if expired else datetime.utcnow() + timedelta(hours=1)
    reset = PasswordResetTokenCustomerBase(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        token=token,
        expires_at=expires_at
    )
    session.add(reset)
    session.commit()
    return reset


# --- Tests ---
def test_forget_password_success(client, db_session):
    customer = seed_customer(db_session)
    response = client.post("/customer/forget_password", json={"email": customer.email})
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["message"] == "Check your email for reset link"


def test_forget_password_not_found(client):
    response = client.post("/customer/forget_password", json={"email": "unknown@example.com"})
    assert response.status_code == 404

def test_reset_password_success(client, db_session):
    customer = seed_customer(db_session)
    reset = seed_reset_token(db_session, customer.id, token="resettoken")

    old_hashed = customer.password

    payload = {
        "token": reset.token,
        "new_password": "newpass123",
        "confirm_password": "newpass123"
    }
    response = client.post("/customer/reset_password", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset successfully"

    db = SessionLocal()
    updated_customer = db.query(CustomerBase).filter(CustomerBase.id == customer.id).first()

    assert pwd_context.verify("newpass123", updated_customer.password)
    assert not pwd_context.verify("oldpass123", updated_customer.password)

    db.close()



def test_reset_password_mismatch(client, db_session):
    customer = seed_customer(db_session)
    reset = seed_reset_token(db_session, customer.id, token="resettoken2")

    payload = {
        "token": reset.token,
        "new_password": "pass1",
        "confirm_password": "pass2"
    }
    response = client.post("/customer/reset_password", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Passwords do not match"


def test_reset_password_invalid_token(client, db_session):
    customer = seed_customer(db_session)

    payload = {
        "token": "invalidtoken",
        "new_password": "pass123",
        "confirm_password": "pass123"
    }
    response = client.post("/customer/reset_password", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid token"


def test_reset_password_expired_token(client, db_session):
    customer = seed_customer(db_session)
    reset = seed_reset_token(db_session, customer.id, token="expiredtoken", expired=True)

    payload = {
        "token": reset.token,
        "new_password": "pass123",
        "confirm_password": "pass123"
    }
    response = client.post("/customer/reset_password", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Token expired"
