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
from sqlalchemy import Column, DateTime, String, Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from auth import create_token, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, get_current_user
from role import StatusCode
from jose import JWTError, jwt
from security.security import verify_password, hash_password
from middleware import AuthMiddleware
from datetime import datetime
import logging

# Cấu hình logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

URL_DATABASE = "postgresql://postgres:Revive@localhost:5432/db_3"
engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class EmployeeBase(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True, index=True)
    employee_name = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False, index=True)
    email = Column(String, index=True)
    is_active = Column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AccountBase(Base):
    __tablename__ = "employee_register_information"

    id = Column(String, primary_key=True, nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    password = Column(String, index=True, nullable=False)
    role = Column(String, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class AccountSchema(BaseModel):
    email: str = Field(..., description='Please input the email!')
    password: str = Field(..., description='Please input the password!')
    remember: bool = Optional

class EmployeeSignUpSchema(BaseModel):
    id: Optional[str] = None
    email: str
    password: str
    confirmPassword: str
    role: str

class EmployeeSchema(BaseModel):
    id: Optional[str] = None
    employee_name: str
    role: str
    email: str
    is_active: bool

class EmployeeInputSchema(BaseModel):
    employee_name: str
    role: str
    email: str
    is_active: bool

class SuccessMessageSchema(BaseModel):
    message: str

class SearchResultBase(BaseModel):
    message: str
    search_result: List[EmployeeSchema]
    employee_count: int
    total_employee: int

class SavingEmployeeUpdateSchema(BaseModel):
    employee_name: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[int] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

app = FastAPI(title='Demo employee', version='1.0')
app.add_middleware(AuthMiddleware)

origins = ['http://localhost:5173']

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.get("/me")
def get_account(current_user: dict = Depends(get_current_user)):
    return current_user
    
#Get and search employee
@app.get("/employees")
def search_employee(
    search_id: str | None = Query(None, description="Search by ID"),
    search_employee: str | None = Query(None, description="Search by Employee Name"),
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    created_at: str = None,
    employee_id: str = None,
    db: Session = Depends(get_db),
    account_info: dict = Depends(get_account)
):
    account_role = account_info.get("role")
    if account_role not in 'admin':
        raise HTTPException(status_code=StatusCode.HTTP_FORBIDDEN_403.value, detail="You are not allowed to access to this data!")
    # Example: verify dependencies return valid data
    if not account_info:
        raise HTTPException(status_code=StatusCode.HTTP_UNAUTHORIZE_401.value, detail="Unauthorized")
    # Example query logic
    total_employee = len(db.query(EmployeeBase).all())
    employees = (
        db.query(EmployeeBase)
        .filter(EmployeeBase.id.contains(search_id) if search_id else True)
        .filter(EmployeeBase.name.contains(search_employee) if search_employee else True)
        .limit(limit)
        .all()
    )
    if(created_at and employee_id):
        employees = (db.query(EmployeeBase).where(EmployeeBase.created_at == created_at and EmployeeBase.id <= employee_id or EmployeeBase.created_at < created_at).order_by(EmployeeBase.id.desc(), EmployeeBase.created_at.desc()))
    items = db.query(EmployeeBase).limit(limit).all()

    # Compute next_cursor from the last record
    next_cursor = None
    if items:
        last = items[-1]
        next_cursor = {"date": last.created_at, "id": last.id}
        logger.info(last)

    return {
        'message': 'Search successfully',
        'search_result': employees,
        'employee_count': len(employees),
        'total_employee': total_employee,
        'next_cursor': next_cursor
    }

@app.post('/signup')
def sign_up(account_info: EmployeeSignUpSchema, db: Session = Depends(get_db)):
    account_filter = db.query(AccountBase).filter(AccountBase.email == account_info.email).first()
    if account_filter is not None:
        raise HTTPException(status_code=400, detail="employee has already existed!")
    elif account_info.password != account_info.confirmPassword:
        raise HTTPException(status_code=400, detail="Password did not match")
    account = AccountBase(
        id = str(uuid.uuid4()),
        email = account_info.email,
        password = hash_password(account_info.password),
        role = account_info.role,
        created_at=datetime.utcnow()
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return {"message": "Sign up successfully"}

@app.post('/login')
def login(employee_info: AccountSchema, db: Session = Depends(get_db)):
    employee = db.query(AccountBase).filter(AccountBase.email == employee_info.email).first()
    if not employee:
        raise HTTPException(status_code=StatusCode.HTTP_ERROR_404, detail="employee not found")
    if not verify_password(employee_info.password, employee.password):
        raise HTTPException(status_code=StatusCode.HTTP_UNAUTHORIZE_401.value, detail="Incorrect password")
    
    access_token = create_token({"sub": employee_info.email, "role": employee.role}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_token({"sub": employee_info.email, "role": employee.role}, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    a = get_account()
    logger.info(a)
    return {
        "message": "Register successfully",
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@app.post("/refresh")
def refresh_token(authorization: str = Header(None)):
    if not authorization:
        return JSONResponse(status_code=StatusCode.HTTP_UNAUTHORIZE_401.value, content={"message": "Missing refresh token"})

    refresh_token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(refresh_token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        email = payload.get("sub")
        new_access_token = create_token(
            {"sub": email}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": new_access_token}
    except jwt.ExpiredSignatureError:
        return JSONResponse(status_code=StatusCode.HTTP_UNAUTHORIZE_401.value, content={"message": "Refresh token expired"})
    except JWTError:
        return JSONResponse(status_code=StatusCode.HTTP_UNAUTHORIZE_401.value, content={"message": "Invalid refresh token"})
    

#Get detail employee
@app.get('/employee/{employeeId}', response_model=EmployeeSchema)
def get_employee_detail(employeeId: str, db: Session = Depends(get_db)):
    employee = db.query(EmployeeBase).filter(EmployeeBase.id == employeeId).first()
    if not employee:
        raise HTTPException(status_code=404, detail='Employee not found')
    return employee
    
@app.post('/employees', response_model=SuccessMessageSchema)
def create_employee(employee: EmployeeInputSchema, db: Session = Depends(get_db)):
    new_employee = EmployeeBase(
        id=str(uuid.uuid4()),
        employee_name = employee.employee_name,
        role = employee.role,
        email = employee.email,
        is_active = employee.is_active,
        created_at=datetime.utcnow()
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return SuccessMessageSchema(message='employee created successfully')

@app.delete('/employee/{employeeId}', response_model=SuccessMessageSchema)
def delete_employee(employeeId: str, db: Session = Depends(get_db)):
    delete_user = db.query(EmployeeBase).filter(EmployeeBase.id == employeeId).first()
    if delete_user:
        db.delete(delete_user)
        db.commit()
        return {'message': 'employee deleted successfully'}
    raise HTTPException(status_code=StatusCode.HTTP_ERROR_404, detail='employee not found')

@app.put('/employee/{employeeId}', response_model=SuccessMessageSchema)
def update_employee(
    employeeId: str,
    employee_update_data: SavingEmployeeUpdateSchema,
    db: Session = Depends(get_db)
):
    update_user = db.query(EmployeeBase).filter(EmployeeBase.id == employeeId).first()
    if not update_user:
        raise HTTPException(status_code=StatusCode.HTTP_ERROR_404, detail='employee not found')
    
    # Update giá trị vào SQLAlchemy model
    for key, value in employee_update_data.dict(exclude_unset=True).items():
        setattr(update_user, key, value)
    
    db.commit()   # lưu vào DB
    db.refresh(update_user)  # cập nhật lại object nếu cần
    
    return SuccessMessageSchema(message='employee updated successfully!')

        

if __name__ == '__main__':
    uvicorn.run('main:app', port=8080, reload=True)



