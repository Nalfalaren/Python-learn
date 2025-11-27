from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from .models import OrderItem
from apis.orders.models import OrderBase
from .schema import CheckoutPayload
orders_item_router = APIRouter(tags=['Order Item'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@orders_item_router.post("/checkout")
def checkout(
    payload: CheckoutPayload, 
    db: Session = Depends(get_db)
):
    customer_info = payload.customer
    cart_info = payload.cart
    # Lưu order
    order = OrderBase(
        customer_name=customer_info["name"],
        email=customer_info["email"],
        phone=customer_info["phone"],
        address=customer_info["address"],
        status="PENDING"
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Lưu chi tiết sản phẩm
    for item in cart_info:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product_id"],
            product_name=item["product_name"],
            qty=item["qty"],
            price=item["price"]
        )
        db.add(order_item)
    db.commit()
    return {"message": "Order placed successfully", "order_id": order.id}
