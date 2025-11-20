from typing import List, Optional
from pydantic import BaseModel

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