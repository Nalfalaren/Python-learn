from datetime import timedelta
import os
from fastapi import FastAPI, HTTPException, Header, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, List, Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import uvicorn
import uuid
from sqlalchemy import Column, String, Float, Integer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from auth import create_token, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from jose import JWTError, jwt
from security.security import verify_password, hash_password
from middleware import AuthMiddleware

URL_DATABASE = "postgresql://postgres:Revive@localhost:5432/db_3"
engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class SavingAccountBase(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, index=True)
    owner = Column(String, index=True)
    balance = Column(Float, default=0.0)
    interest_rate = Column(Float, default=0.0)
    max_withdraw_count = Column(Integer, default=0)

class AdminAccountSchemaBase(Base):
    __tablename__ = "account_information"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, index=True)
    password = Column(String, index=True)


Base.metadata.create_all(bind=engine)

class AdminAccountSchema(BaseModel):
    id: str = Optional
    email: str
    password: str
    remember: bool = Optional

class AdminAccountSignUpSchema(BaseModel):
    id: str = Optional
    email: str
    password: str
    confirmPassword: str

class SavingAccountSchema(BaseModel):
    id: str
    owner: str
    balance: float = Field(..., ge=0)
    interest_rate: float = Field(..., ge=0, description='Interest rate must higher than 0%')
    max_withdraw_count: int = Field(..., description='Max withdraw must be included!')

class SavingAccountInputSchema(BaseModel):
    owner: str

class SuccessMessageSchema(BaseModel):
    message: str

class SearchResultBase(BaseModel):
    message: str
    search_result: List[SavingAccountSchema]
    accounts_count: int

class SavingAccountUpdateSchema(BaseModel):
    owner: Optional[str] = None
    balance: Optional[float] = None
    interest_rate: Optional[float] = None
    max_withdraw_count: Optional[int] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

app = FastAPI(title='Demo account', version='1.0')
app.add_middleware(AuthMiddleware)

origins = ['http://localhost:5173']

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

#Get and search account
@app.get('/account', response_model=SearchResultBase)
def search_account(
    search_id: str = Query(None, description='Search by ID'),
    search_account: str = Query(None, description='Search by Account Name'),
    db: Session = Depends(get_db)
):
    query = db.query(SavingAccountBase)

    # Apply filters dynamically
    if search_id:
        query = query.filter(SavingAccountBase.id == search_id)
    if search_account:
        query = query.filter(SavingAccountBase.owner == search_account)

    results = query.all()
    return {
        'message': 'Search successful',
        'search_result': results,
        'accounts_count': len(results)
    }

@app.post('/sign-up')
def sign_up(account_info: AdminAccountSignUpSchema, db: Session = Depends(get_db)):
    account_filter = db.query(AdminAccountSchemaBase).filter(AdminAccountSchemaBase.email == account_info.email).first()
    if account_filter is not None:
        raise HTTPException(status_code=400, detail="Account has already existed!")
    elif account_info.password != account_info.confirmPassword:
        raise HTTPException(status_code=400, detail="Password did not match")
    
    account = AdminAccountSchemaBase(
        id = str(uuid.uuid4()),
        email = account_info.email,
        password = hash_password(account_info.password)
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return {"message": "Sign up successfully"}

@app.post('/login')
def login(account_info: AdminAccountSchema, db: Session = Depends(get_db)):
    account = db.query(AdminAccountSchemaBase).filter(AdminAccountSchemaBase.email == account_info.email).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if not verify_password(account_info.password, account.password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    access_token = create_token({"sub": account_info.email}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_token({"sub": account_info.email}, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
        
    return {
        "message": "Register successfully",
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@app.post("/refresh")
def refresh_token(authorization: str = Header(None)):
    if not authorization:
        return JSONResponse(status_code=401, content={"message": "Missing refresh token"})

    refresh_token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(refresh_token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        email = payload.get("sub")
        new_access_token = create_token(
            {"sub": email}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": new_access_token}
    except jwt.ExpiredSignatureError:
        return JSONResponse(status_code=401, content={"message": "Refresh token expired"})
    except JWTError:
        return JSONResponse(status_code=401, content={"message": "Invalid refresh token"})
    

#Get detail account
@app.get('/account/{accountId}', response_model=SavingAccountSchema)
def get_account_detail(accountId: str, db: Session = Depends(get_db)):
    account = db.query(SavingAccountBase).filter(SavingAccountBase.id == accountId).first()
    if not account:
        raise HTTPException(status_code=404, detail='Account not found')
    return account
    
@app.post('/account', response_model=SuccessMessageSchema)
def create_account(account: SavingAccountInputSchema, db: Session = Depends(get_db)):
    new_account = SavingAccountBase(
        id=str(uuid.uuid4()),
        owner=account.owner,
        balance=0.0,
        interest_rate=5,
        max_withdraw_count=3
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return SuccessMessageSchema(message='Account created successfully')

@app.delete('/account/{accountId}', response_model=SuccessMessageSchema)
def delete_account(accountId: str, db: Session = Depends(get_db)):
    delete_user = db.query(SavingAccountBase).filter(SavingAccountBase.id == accountId).first()
    if delete_user:
        db.delete(delete_user)
        db.commit()
        return {'message': 'Account deleted successfully'}
    raise HTTPException(status_code=404, detail='Account not found')

@app.put('/account/{accountId}', response_model=SuccessMessageSchema)
def update_account(
    accountId: str,
    account_update_data: SavingAccountUpdateSchema,
    db: Session = Depends(get_db)
):
    update_user = db.query(SavingAccountBase).filter(SavingAccountBase.id == accountId).first()
    if not update_user:
        raise HTTPException(status_code=404, detail='Account not found')
    
    # Update giá trị vào SQLAlchemy model
    for key, value in account_update_data.dict(exclude_unset=True).items():
        setattr(update_user, key, value)
    
    db.commit()   # lưu vào DB
    db.refresh(update_user)  # cập nhật lại object nếu cần
    
    return SuccessMessageSchema(message='Account updated successfully!')

        

if __name__ == '__main__':
    uvicorn.run('main:app', port=8080, reload=True)



