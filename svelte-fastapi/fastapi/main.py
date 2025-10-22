from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import uvicorn
import uuid
from sqlalchemy import Column, String, Float, Integer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# URL_DATABASE = "postgresql://postgres:Revive@localhost:8000/account_database"
# URL_DATABASE = "postgresql://postgres:Revive@localhost:5432/mydatabase"
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

Base.metadata.create_all(bind=engine)


class SavingAccount(BaseModel):
    id: str
    owner: str
    balance: float = Field(..., ge=0)
    interest_rate: float = Field(..., ge=0, description='Interest rate must higher than 0%')
    max_withdraw_count: int = Field(..., description='Max withdraw must be included!')

class SavingAccountInput(BaseModel):
       owner: str

class SuccessMessageBase(BaseModel):
    message: str

class SearchResultBase(BaseModel):
    message: str
    search_result: List[SavingAccount]
    accounts_count: int

class SavingAccountUpdate(BaseModel):
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

#Get detail account
@app.get('/account/{accountId}', response_model=SavingAccount)
def get_account_detail(accountId: str, db: Session = Depends(get_db)):
    account = db.query(SavingAccountBase).filter(SavingAccountBase.id == accountId).first()
    if not account:
        raise HTTPException(status_code=404, detail='Account not found')
    return account
    
@app.post('/account', response_model=SuccessMessageBase)
def create_account(account: SavingAccountInput, db: Session = Depends(get_db)):
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
    return SuccessMessageBase(message='Account created successfully')

@app.delete('/account/{accountId}', response_model=SuccessMessageBase)
def delete_account(accountId: str, db: Session = Depends(get_db)):
    delete_user = db.query(SavingAccountBase).filter(SavingAccountBase.id == accountId).first()
    if delete_user:
        db.delete(delete_user)
        db.commit()
        return {'message': 'Account deleted successfully'}
    raise HTTPException(status_code=404, detail='Account not found')

@app.put('/account/{accountId}', response_model=SuccessMessageBase)
def update_account(
    accountId: str,
    account_update_data: SavingAccountUpdate,
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
    
    return SuccessMessageBase(message='Account updated successfully!')

        

if __name__ == '__main__':
    uvicorn.run('main:app', port=8080, reload=True)



