from datetime import datetime
import enum
from typing import Any, Optional
from pydantic import BaseModel

class OrderStatusEnum(str, enum.Enum):
    pending = "Pending"
    processing = "Processing"
    shipped = "Shipped"
    completed = "Completed"
    cancelled = "Cancelled"

class OrderSchema(BaseModel):
    id: str
    customer_name: str
    email: str
    phone: str
    address: str
    status: OrderStatusEnum
    created_at: Optional[datetime] = None
    items: Any

class CheckoutPayload(BaseModel):
    customer: dict
    cart: list[Any]