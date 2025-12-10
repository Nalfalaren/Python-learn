from typing import Optional
from pydantic import BaseModel, Field

class AccountSchema(BaseModel):
    email: str = Field(..., description='Please input the email!')
    password: str = Field(..., description='Please input the password!')
    remember: bool = Optional

class EmployeeSignUpSchema(BaseModel):
    id: Optional[str] = None
    employee_name: str
    email: str
    password: str
    confirmPassword: str
    role: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str