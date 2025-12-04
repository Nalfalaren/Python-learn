from datetime import datetime, timedelta
import logging
import os
from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from database import SessionLocal
from apis.login.models import AdminBase
from .utils import generate_token, hash_password
from .models import PasswordResetTokenEmployeeBase
from .schema import RequestEmail, ResetPasswordRequestPayload
employee_router = APIRouter(prefix="/employee", tags=["Authentication"])
load_dotenv()

# Database Dependency 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# Logger 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@employee_router.post("/forget_password")
def forget_password(request: RequestEmail, db: Session = Depends(get_db)):
    email = request.email
    account = db.query(AdminBase).filter(AdminBase.email == email).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found!")
    
    token = generate_token()
    expires_at = datetime.utcnow() + timedelta(hours=1)
    reset_token = PasswordResetTokenEmployeeBase(id=str(uuid.uuid4()), employee_id=account.id, token=token, expires_at=expires_at)
    db.add(reset_token)
    db.commit()

    return {
        "message": "Check your email for reset link",
        "token": token
    }

@employee_router.post("/reset_password")
def reset_password(request: ResetPasswordRequestPayload, db: Session = Depends(get_db)):
    new_password = request.new_password
    confirm_password = request.confirm_password
    
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    reset = db.query(PasswordResetTokenEmployeeBase).filter(
        PasswordResetTokenEmployeeBase.token == request.token
    ).first()

    if not reset:
        raise HTTPException(status_code=400, detail="Invalid token")

    if reset.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired")

    user = db.query(AdminBase).filter(
        AdminBase.id == reset.employee_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hash_password(new_password)
    db.delete(reset)
    db.commit()

    return {"message": "Password reset successfully"}
    


