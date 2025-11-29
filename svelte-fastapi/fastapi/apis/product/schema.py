from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ProductSchema(BaseModel):
    id: Optional[str] = None
    product_name: str
    category: str
    price: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SuccessMessageSchema(BaseModel):
    message: str

class ProductUpdatePropsSchema(BaseModel):
    product_name: str
    category: str
    price: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None