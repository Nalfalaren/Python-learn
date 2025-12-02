import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from .models import OrderItem
from apis.orders.models import OrderBase
from .schema import CheckoutPayload
from .repository import get_order_items_query
from auth import get_current_user, require_admin
order_items_router = APIRouter(tags=['Order Item'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@order_items_router.get("/me")
def get_account(current_user: dict = Depends(get_current_user)):
    return current_user

@order_items_router.post("/checkout")
def checkout(payload: CheckoutPayload, db: Session = Depends(get_db)):
    customer_info = payload.customer
    cart_info = payload.cart

    order = OrderBase(
        id=str(uuid.uuid4()), 
        customer_name=customer_info["name"],
        email=customer_info["email"],
        phone=customer_info["phone"],
        address=customer_info["address"],
        employee_id=None, 
        status="PENDING"
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Lưu chi tiết sản phẩm
    for item in cart_info:
        order_item = OrderItem(
            id=str(uuid.uuid4()),
            order_id=order.id, 
            product_id=item["product_id"],
            product_name=item["product_name"],
            qty=item["qty"],
            price=item["price"]
        )
        db.add(order_item)

    db.commit()
    return {"message": "Order placed successfully", "order_id": str(order.id)}

@order_items_router.get("/order_items")
def get_order_items(page: int = 1, limit: int = 10, order_id: str = "", id: str = "", db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    order_items = get_order_items_query(db)
    if(order_id):
        order_items = order_items.filter(OrderItem.order_id == order_id)
    elif(id):
        order_items = order_items.filter(OrderBase.id == id)
    total_orders = order_items.count() 
    offset = (page - 1) * limit
    paginated_orders = order_items.offset(offset).limit(limit).all()
    result = []

    for order in paginated_orders:
        result.append({
            "id": order.id,
            "order_id": order.order_id,
            "product_id": order.product_id,
            "product_name": order.product_name,
            "qty": order.qty,
            "price": order.price,
        })
    return {
        "search_result": result,
        "items_count": total_orders,
        "page": page,
        "limit": limit,
        "total_pages": (total_orders + limit - 1)
    }