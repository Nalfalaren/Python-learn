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
from sqlalchemy import Column, String, Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from auth import create_token, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from jose import JWTError, jwt
from security.security import verify_password, hash_password
from middleware import AuthMiddleware
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

class employeeBase(Base):
    __tablename__ = "employee_register_information"

    id = Column(String, primary_key=True, nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    password = Column(String, index=True, nullable=False)


Base.metadata.create_all(bind=engine)

class employeeSchema(BaseModel):
    id: Optional[str] = None
    email: str = Field(..., description='Please input the email!')
    password: str = Field(..., description='Please input the password!')
    remember: bool = Optional

class employeeSignUpSchema(BaseModel):
    id: Optional[str] = None
    email: str
    password: str
    confirmPassword: str

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

#Get and search employee
@app.get('/employees', response_model=SearchResultBase)
def search_employee(
    search_id: str = Query(None, description='Search by ID'),
    search_employee: str = Query(None, description='Search by Employee Name'),
    page: int = Query(10, ge=1, description='Choose page'),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):    
    query = db.query(EmployeeBase)

    # Apply filters dynamically
    if search_id:
        query = query.filter(EmployeeBase.id == search_id)
    if search_employee:
        query = query.filter(EmployeeBase.employee_name == search_employee)

    offset = (page - 1) * limit
    total_employee = len(query.all())
    results = query.offset(offset=offset).limit(limit).all()
    return {
        'message': 'Search successfully',
        'search_result': results,
        'employee_count': len(results),
        'total_employee': total_employee
    }

@app.post('/signup')
def sign_up(employee_info: employeeSignUpSchema, db: Session = Depends(get_db)):
    employee_filter = db.query(employeeBase).filter(employeeBase.email == employee_info.email).first()
    if employee_filter is not None:
        raise HTTPException(status_code=400, detail="employee has already existed!")
    elif employee_info.password != employee_info.confirmPassword:
        raise HTTPException(status_code=400, detail="Password did not match")
    
    employee = employeeBase(
        id = str(uuid.uuid4()),
        email = employee_info.email,
        password = hash_password(employee_info.password)
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return {"message": "Sign up successfully"}

@app.post('/login')
def login(employee_info: employeeSchema, db: Session = Depends(get_db)):
    employee = db.query(employeeBase).filter(employeeBase.email == employee_info.email).first()
    if not employee:
        raise HTTPException(status_code=404, detail="employee not found")
    if not verify_password(employee_info.password, employee.password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    access_token = create_token({"sub": employee_info.email}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_token({"sub": employee_info.email}, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
        
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
        is_active = employee.is_active
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
    raise HTTPException(status_code=404, detail='employee not found')

@app.put('/employee/{employeeId}', response_model=SuccessMessageSchema)
def update_employee(
    employeeId: str,
    employee_update_data: SavingEmployeeUpdateSchema,
    db: Session = Depends(get_db)
):
    update_user = db.query(EmployeeBase).filter(EmployeeBase.id == employeeId).first()
    if not update_user:
        raise HTTPException(status_code=404, detail='employee not found')
    
    # Update giá trị vào SQLAlchemy model
    for key, value in employee_update_data.dict(exclude_unset=True).items():
        setattr(update_user, key, value)
    
    db.commit()   # lưu vào DB
    db.refresh(update_user)  # cập nhật lại object nếu cần
    
    return SuccessMessageSchema(message='employee updated successfully!')

        

if __name__ == '__main__':
    uvicorn.run('main:app', port=8080, reload=True)



