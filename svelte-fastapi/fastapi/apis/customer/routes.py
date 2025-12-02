from datetime import datetime
from typing import Annotated, Optional
from passlib.hash import argon2 
from fastapi import APIRouter, HTTPException, Depends
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
from sqlalchemy.orm import load_only

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

@router.get("/customers")
def get_customers(
    limit: int = 10,
    search_id: Optional[str] = None,
    search_name: Optional[str] = None,
    next_cursor: Optional[str] = None,
    db: Session = Depends(get_db)
):

    query = db.query(CustomerBase).options(load_only(
        CustomerBase.id,
        CustomerBase.customer_name,
        CustomerBase.email,
        CustomerBase.role
    ))

    # Search Filters
    if search_id:
        query = query.filter(CustomerBase.id == search_id)
    if search_name:
        query = query.filter(CustomerBase.customer_name.ilike(f"%{search_name}%"))

    # Cursor pagination
    if next_cursor:
        query = query.filter(CustomerBase.id > next_cursor)

    customers = query.order_by(CustomerBase.id).limit(limit + 1).all()

    # Tính next cursor
    if len(customers) > limit:
        next_cursor_value = customers[-1].id
        customers = customers[:limit]
    else:
        next_cursor_value = None

    total = db.query(CustomerBase).count()

    return {
        "search_result": customers,
        "next_cursor": next_cursor_value,
        "total_employee": total
    }

@router.get("/customers/{id}")
def get_customer_detail(id: str, db: Session = Depends(get_db)):
    customer = db.query(CustomerBase).options(load_only(
        CustomerBase.id,
        CustomerBase.customer_name,
        CustomerBase.phone,
        CustomerBase.address,
        CustomerBase.email,
        CustomerBase.is_active,
        CustomerBase.role
    )).filter(CustomerBase.id == id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.delete("/customers/{id}")
def delete_customer(id: str, db: Session = Depends(get_db)):

    customer = db.query(CustomerBase).filter(CustomerBase.id == id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(customer)
    db.commit()

    return {"message": "Customer deleted successfully"}
