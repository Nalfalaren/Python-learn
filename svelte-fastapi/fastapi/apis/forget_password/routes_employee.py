from datetime import datetime, timedelta
import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from database import SessionLocal
from apis.login.models import AccountBase
from .utils import generate_token, hash_password
from .models import PasswordResetTokenCustomerBase
from .schema import RequestEmail
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
    account = db.query(AccountBase).filter(AccountBase.email == email).first()
    if not account:
        return HTTPException(status_code=404, detail="Account not found!")
    
    token = generate_token()
    expires_at = datetime.utcnow() + timedelta(hours=1)
    reset_token = PasswordResetTokenCustomerBase(user_id=account.id, token=token, expires_at=expires_at)
    db.add(reset_token)
    db.commit()

    return {"message": "Check your email for reset link"}

@employee_router.post("/reset_password")
def reset_password(token: str, new_password: str, confirm_password: str, db: Session = Depends(get_db)):
    if new_password != confirm_password:
        raise HTTPException(400, "Passwords do not match")

    reset = db.query(PasswordResetTokenCustomerBase).filter(PasswordResetTokenCustomerBase.token == token).first()
    if not reset or reset.expires_at < datetime.utcnow():
        raise HTTPException(400, "Invalid or expired token")

    user = db.query(AccountBase).filter(AccountBase.id == reset.user_id).first()
    user.password = hash_password(new_password)
    db.delete(reset)
    db.commit()

    return {"message": "Password reset successfully"}
    


