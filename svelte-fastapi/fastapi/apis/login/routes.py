import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from passlib.hash import argon2  # ✅ use passlib for Argon2
from dotenv import load_dotenv

from role import StatusCode
from .models import AccountBase
from .schema import EmployeeSignUpSchema, AccountSchema
from database import SessionLocal
from auth import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, create_token, handle_login_role

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
        password=argon2.hash(account_info.password),  # ✅ use passlib
        role=account_info.role,
        created_at=datetime.utcnow(),
    )
    db.add(account)
    db.commit()
    db.refresh(account)

    return {"message": "✅ Sign up successful"}

# === Login ===
@router.post("/login")
def login(employee_info: AccountSchema, db: Session = Depends(get_db)):
    employee = db.query(AccountBase).filter(AccountBase.email == employee_info.email).first()
    if not employee:
        raise HTTPException(status_code=StatusCode.HTTP_ERROR_404.value, detail="Employee not found")
    if not argon2.verify(employee_info.password, employee.password):
        raise HTTPException(status_code=StatusCode.HTTP_UNAUTHORIZE_401.value, detail="Incorrect password")
    
    access_token = handle_login_role(employee)['access_token']
    refresh_token = handle_login_role(employee)['refresh_token']

    return {
        "message": "✅ Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
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
