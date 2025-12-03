from datetime import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from database import SessionLocal
from apis.login.models import AccountBase
from .models import OrderBase
from role import StatusCode
from auth import get_current_user, require_admin, require_employee
from sqlalchemy.orm import Session
from .schema import AssignOrderRequest, OrderUpdateSchema
from apis.product.models import ProductBase
from apis.orders_item.models import OrderItem
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
    _: dict = Depends(require_employee),
    db: Session = Depends(get_db),
    search_id: str = '',
    customer_name: str = '',
    employee_id: str = '',
    page: int = 1,
    limit: int = 10,
):
    order_list = db.query(OrderBase).order_by(OrderBase.created_at.desc())
    
    # SỬA LẠI - PHẢI GÁN LẠI KẾT QUẢ
    if employee_id: 
        order_list = order_list.filter(OrderBase.employee_id == employee_id)
    elif search_id:
        order_list = order_list.filter(OrderBase.id == search_id)
    elif customer_name:
        order_list = order_list.filter(func.lower(OrderBase.customer_name).like(f"%{customer_name.lower()}%"))
    
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
            "assign_to": order.assigned_to,
            "total": sum(i.qty * i.price for i in order.items)
        })
    
    return {
        "search_result": result,
        "orders_count": total_orders,
        "page": page,
        "limit": limit,
        "total_pages": (total_orders + limit - 1) // limit
    }

@order_router.get('/orders/{order_id}')
def get_order_detail(order_id: str, db: Session = Depends(get_db), _: dict = Depends(require_employee)):
    order_info = db.query(OrderBase).filter(OrderBase.id == order_id).first()
    if not order_info:
        return HTTPException(status_code=StatusCode.HTTP_ERROR_404, detail="Order not found")
    items = [
        {"product_id": i.product_id, "product_name": i.product_name, "qty": i.qty, "price": i.price}
        for i in order_info.items
    ]
    return {"order": order_info, "items": items}

@order_router.put("/orders/{order_id}")
def update_order_info(
    order_id: str, 
    order: OrderUpdateSchema, 
    db: Session = Depends(get_db), 
    _: dict = Depends(require_employee)
):
    order_info = db.query(OrderBase).filter(OrderBase.id == order_id).first()
    if not order_info:
        raise HTTPException(status_code=404, detail="Order not found")

    # Cập nhật các field được gửi
    for k, v in order.dict(exclude_unset=True).items():
        setattr(order_info, k, v)
    order_info.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order_info)

    if order_info.status == "CANCELLED":
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        for item in order_items:
            product = db.query(ProductBase).filter(ProductBase.id == item.product_id).first()
            if product:
                product.stock += item.qty
            else:
                db.rollback()
                raise HTTPException(
                    status_code=404,
                    detail=f"Product '{item.product_name}' not found"
                )
        db.commit() 

    return {"message": "Order updated"}


@order_router.delete("/orders/{order_id}")
def delete_product(order_id: str, db: Session = Depends(get_db), _: dict = Depends(require_employee)):
    order_info = db.query(OrderBase).filter(OrderBase.id == order_id).first()
    if not order_info:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(order_info)
    db.commit()
    return {"message": "Delete order successfully"}

@order_router.post("/orders/{order_id}/assign")
def assign_order(request: AssignOrderRequest, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    order_id = request.order_id
    employee_id = request.employee_id
    order = db.query(OrderBase).filter(OrderBase.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")

    employee = db.query(AccountBase).filter(AccountBase.id == employee_id).first()
    employee_name = db.query(AccountBase).with_entities(AccountBase.employee_name).filter(AccountBase.id == employee_id).scalar()   

    if not employee:
        raise HTTPException(404, "Employee not found")

    if employee.role != "EMPLOYEE":
        raise HTTPException(400, "Only employees can be assigned orders")

    order.employee_id = employee_id
    order.status = 'ASSIGNED'
    order.assigned_to = employee_name
    db.commit()
    db.refresh(order)
    return order
