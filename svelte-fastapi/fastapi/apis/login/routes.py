import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from passlib.hash import argon2 
from dotenv import load_dotenv

from role import StatusCode
from .models import AccountBase
from apis.customer.models import CustomerBase
from .schema import EmployeeSignUpSchema, AccountSchema
from database import SessionLocal
from auth import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, create_token, get_current_user, handle_login_role

router = APIRouter(prefix='/auth', tags=["Authentication"])
load_dotenv()

# === Database Dependency ===
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# === Logger ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Sign Up ===
@router.post("/signup")
def sign_up(account_info: EmployeeSignUpSchema, db: Session = Depends(get_db)):
    existing = db.query(AccountBase).filter(AccountBase.email == account_info.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee already exists!")
    if account_info.password != account_info.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    account = AccountBase(
        id=str(uuid.uuid4()),
        email=account_info.email,
        employee_name=account_info.employee_name,
        password=argon2.hash(account_info.password),  # ✅ use passlib
        role=account_info.role,
        created_at=datetime.utcnow(),
        is_active = 'Inactive'
    )
    db.add(account)
    db.commit()
    db.refresh(account)

    return {"message": "✅ Sign up successfully"}

# === Login ===
@router.post("/login")
def login(employee_info: AccountSchema, db: Session = Depends(get_db)):
    employee = db.query(AccountBase).filter(AccountBase.email == employee_info.email).first()
    if not employee:
        raise HTTPException(status_code=StatusCode.HTTP_ERROR_404.value, detail="Employee not existed!")
    
    if not argon2.verify(employee_info.password, employee.password):
        raise HTTPException(status_code=StatusCode.HTTP_UNAUTHORIZE_401.value, detail="Incorrect password")

    employee.is_active = "Active"
    db.commit()
    db.refresh(employee)

    tokens = handle_login_role(employee)

    return {
        "message": "✅ Login successful",
        "access_token": tokens['access_token'],
        "refresh_token": tokens['refresh_token'],
        "role": employee.role
    }


# === Refresh Token ===
@router.post("/refresh")
def refresh_token(authorization: str = Header(None)):
    if not authorization:
        return JSONResponse(
            status_code=StatusCode.HTTP_UNAUTHORIZE_401.value,
            content={"message": "Missing refresh token"},
        )

    refresh_token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(refresh_token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        email = payload.get("sub")
        new_access_token = create_token(
            {"sub": email}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": new_access_token}
    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=StatusCode.HTTP_UNAUTHORIZE_401.value,
            content={"message": "Refresh token expired"},
        )
    except JWTError:
        return JSONResponse(
            status_code=StatusCode.HTTP_UNAUTHORIZE_401.value,
            content={"message": "Invalid refresh token"},
        )

from pydantic import BaseModel

class LogoutRequest(BaseModel):
    id: str

@router.post("/logout")
def inactive_user_login(
    request: LogoutRequest, 
    db: Session = Depends(get_db),
    account_info = Depends(get_current_user)
):
    account = None
    if account_info['role'] == 'ADMIN' or account_info['role'] == 'EMPLOYEE':
        account = db.query(AccountBase).filter(AccountBase.id == request.id).first()
    elif account_info['role'] == 'CUSTOMER':
        account = db.query(CustomerBase).filter(CustomerBase.id == request.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not existed!")
    
    account.is_active = 'Inactive'
    db.commit() 
    db.refresh(account)
    
    return {"message": "Log out successfully", "user_id": request.id}
        