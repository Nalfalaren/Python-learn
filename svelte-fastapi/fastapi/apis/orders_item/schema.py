from datetime import datetime
import enum
from typing import Any, Optional
from pydantic import BaseModel, Field

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

class OrderItemCreate(BaseModel):
    """Schema để tạo order item mới"""
    order_id: str = Field(..., description="ID của order")
    product_id: str = Field(..., description="ID của product")
    qty: int = Field(..., gt=0, description="Số lượng phải > 0")
    price: Optional[float] = Field(None, ge=0, description="Giá (nếu không truyền sẽ lấy giá hiện tại của product)")

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "550e8400-e29b-41d4-a716-446655440000",
                "product_id": "660e8400-e29b-41d4-a716-446655440000",
                "qty": 2,
                "price": 100000
            }
        }

class OrderItemUpdate(BaseModel):
    """Schema để cập nhật order item"""
    qty: Optional[int] = Field(None, gt=0, description="Số lượng mới")
    price: Optional[float] = Field(None, ge=0, description="Giá mới")

    class Config:
        json_schema_extra = {
            "example": {
                "qty": 5,
                "price": 120000
            }
        }

class OrderItemResponse(BaseModel):
    """Schema response cho order item"""
    id: str
    order_id: str
    product_id: str
    product_name: str
    qty: int
    price: float
    subtotal: float

    class Config:
        from_attributes = True