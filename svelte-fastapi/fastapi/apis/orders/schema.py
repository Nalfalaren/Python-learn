from datetime import datetime
import enum
from typing import Any, Optional
from pydantic import BaseModel

class OrderStatusEnum(str, enum.Enum):
    pending = "PENDING"
    processing = "PROCESSING"
    shipped = "SHIPPED"
    completed = "COMPLETED"
    cancelled = "CANCELLED"

class OrderSchema(BaseModel):
    id: str
    customer_name: str
    email: str
    phone: str
    address: str
    status: OrderStatusEnum
    created_at: Optional[datetime] = None
    items: Any

class OrderUpdateSchema(BaseModel):
    customer_name: str
    email: str
    phone: str
    address: str
    status: OrderStatusEnum
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None