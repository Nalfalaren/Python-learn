from datetime import datetime
from typing import Annotated
from passlib.hash import argon2 
from fastapi import APIRouter, HTTPException, Header, Query, Depends
from sqlalchemy.orm import Session
import uuid
from auth import get_current_user, handle_login_role
import logging
from sqlalchemy.orm import Session
from database import SessionLocal
from .schema import CustomerSignUpSchema
from .models import CustomerBase
from role import StatusCode
from apis.login.schema import AccountSchema
router = APIRouter(tags=["Customers"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# Cấu hình logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/me")
def get_account(current_user: dict = Depends(get_current_user)):
    return current_user

@router.post("/signup")
def sign_up(account_info: CustomerSignUpSchema, db: Session = Depends(get_db)):
    existing = db.query(CustomerBase).filter(CustomerBase.email == account_info.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Customer already exists!")
    if account_info.password != account_info.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    account = CustomerBase(
        id=str(uuid.uuid4()),
        email=account_info.email,
        customer_name=account_info.customer_name,
        password=argon2.hash(account_info.password),
        phone=account_info.phone,
        address=account_info.address,
        created_at=datetime.utcnow(),
        is_active = 'Inactive',
        role = 'CUSTOMER'
    )
    db.add(account)
    db.commit()
    db.refresh(account)

    return {"message": "✅ Sign up successfully"}

# === Login ===
@router.post("/login")
def login(customer_info: AccountSchema, db: Session = Depends(get_db)):
    customer = db.query(CustomerBase).filter(CustomerBase.email == customer_info.email).first()
    if not customer:
        raise HTTPException(status_code=StatusCode.HTTP_ERROR_404.value, detail="Customer not existed!")
    
    if not argon2.verify(customer_info.password, customer.password):
        raise HTTPException(status_code=StatusCode.HTTP_UNAUTHORIZE_401.value, detail="Incorrect password")

    customer.is_active = "Active"
    db.commit()
    db.refresh(customer)

    tokens = handle_login_role(customer)

    return {
        "message": "✅ Login successful",
        "access_token": tokens['access_token'],
        "refresh_token": tokens['refresh_token'],
    }