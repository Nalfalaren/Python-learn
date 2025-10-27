from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os

load_dotenv()

# Secret key để mã hóa
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Tạo token (access hoặc refresh)
def create_token(data: dict, expires_delta: timedelta):
    copy_data = data.copy()
    expired_date = datetime.utcnow() + expires_delta
    copy_data.update({"exp": expired_date})
    new_token = jwt.encode(copy_data, SECRET_KEY, algorithm=ALGORITHM)
    return new_token

# Xác thực token
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # trả lại thông tin user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
