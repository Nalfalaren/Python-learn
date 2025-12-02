from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt, ExpiredSignatureError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
import logging
from role import StatusCode

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
# Create JWT token
def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Verify JWT token and extract payload
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(status_code=StatusCode.HTTP_UNAUTHORIZE_401.value, detail="Token missing expiration")

        if datetime.now(timezone.utc).timestamp() > exp:
            raise HTTPException(status_code=StatusCode.HTTP_UNAUTHORIZE_401.value, detail="Token expired")

        if "sub" not in payload:
            raise HTTPException(status_code=StatusCode.HTTP_UNAUTHORIZE_401.value, detail="Invalid token payload")

        return payload

    except ExpiredSignatureError:
        raise HTTPException(status_code=StatusCode.HTTP_UNAUTHORIZE_401.value, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=StatusCode.HTTP_UNAUTHORIZE_401.value, detail="Invalid token")
    

def get_current_user(token: str = Depends(oauth2_scheme)):
    user_info = verify_token(token)
    return {
        "user_email": user_info.get("sub"),
        "role": user_info.get("role")
    }

def handle_login_role(employee_info: any):
    access_token = create_token(
        {"sub": employee_info.email, "role": employee_info.role, "id": employee_info.id},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token = create_token(
        {"sub": employee_info.email, "role": employee_info.role, "id": employee_info.id},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    return {"access_token": access_token, "refresh_token": refresh_token}

def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def require_employee(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "ADMIN" and current_user.get("role") != 'EMPLOYEE':
        raise HTTPException(status_code=403, detail="Employee access required")
    return current_user