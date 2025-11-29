from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class CustomerSignUpSchema(BaseModel):
    id: Optional[str] = None
    customer_name: str
    email: str
    password: str
    confirmPassword: str
    phone: str
    address: str
    created_at: Optional[datetime] = None
    is_active: str


