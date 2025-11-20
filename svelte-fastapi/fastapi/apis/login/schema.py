from typing import Optional
from pydantic import BaseModel, Field

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
