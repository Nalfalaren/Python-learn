from datetime import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from database import SessionLocal
from .models import OrderBase
from role import StatusCode
from auth import get_current_user
from sqlalchemy.orm import Session
from .schema import OrderUpdateSchema
order_router = APIRouter(tags=["Order Route"])
# Cấu hình logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@order_router.get("/me")
def get_account(current_user: dict = Depends(get_current_user)):
    return current_user

@order_router.get('/orders')
def get_list_orders(
    account_info: dict = Depends(get_account),
    db: Session = Depends(get_db),
    search_id: str = '',
    order_name: str = '',
    page: int = 1,
    limit: int = 10,
):
     # --- Role check ---
    account_role = account_info.get("role")
    if account_role != "admin":
        raise HTTPException(
            status_code=StatusCode.HTTP_FORBIDDEN_403.value,
            detail="You are not allowed to access this data!",
        )
    order_list = db.query(OrderBase).order_by(OrderBase.created_at.desc())
    if search_id:
        order_list = order_list.filter(OrderBase.id == search_id)
    elif order_name:
        order_list = order_list.filter(OrderBase.customer_name == order_name)
    total_orders = order_list.count() 
    offset = (page - 1) * limit
    paginated_orders = order_list.offset(offset).limit(limit).all()
    result = []

    for order in paginated_orders:
        result.append({
            "id": order.id,
            "customer_name": order.customer_name,
            "email": order.email,
            "phone": order.phone,
            "address": order.address,
            "status": order.status,
            "created_at": order.created_at,
            "total": sum(i.qty * i.price for i in order.items)
        })
    return {
        "search_result": result,
        "orders_count": total_orders,
        "page": page,
        "limit": limit,
        "total_pages": (total_orders + limit - 1)
    } 

@order_router.get('/orders/{order_id}')
def get_order_detail(order_id: str, db: Session = Depends(get_db)):
    order_info = db.query(OrderBase).filter(OrderBase.id == order_id).first()
    if not order_info:
        return HTTPException(status_code=StatusCode.HTTP_ERROR_404, detail="Order not found")
    items = [
        {"product_id": i.product_id, "product_name": i.product_name, "qty": i.qty, "price": i.price}
        for i in order_info.items
    ]
    return {"order": order_info, "items": items}

@order_router.put("/orders/{order_id}")
def update_order_info(order_id: str, order: OrderUpdateSchema, db: Session = Depends(get_db)):
    order_info = db.query(OrderBase).filter(OrderBase.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    for k, v in order.dict(exclude_unset=True).items():
        setattr(order_info, k, v)
    order_info.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order_info) 
    return {
        "message": f"Order updated"
    }

@order_router.delete("/orders/{order_id}")
def delete_product(order_id: str, db: Session = Depends(get_db)):
    order_info = db.query(OrderBase).filter(OrderBase.id == order_id).first()
    if not order_info:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(order_info)
    db.commit()
    return {"message": "Delete order successfully"}


@order_router.patch("/orders/{order_id}/status")
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(OrderBase).filter(OrderBase.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    db.commit()
    return {"message": f"Order status updated to {status}"}