import uuid
from fastapi import APIRouter, Depends, HTTPException, status
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
    """Tạo order mới với nhiều items (Checkout)"""
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
    return {
        "message": "Order placed successfully", 
        "order_id": str(order.id)
    }

@order_items_router.get("/order_items")
def get_order_items(
    page: int = 1, 
    limit: int = 10, 
    order_id: str = "", 
    id: str = "", 
    db: Session = Depends(get_db), 
    _: dict = Depends(require_admin)
):
    """Lấy danh sách order items với filter và pagination"""
    order_items = get_order_items_query(db).order_by(OrderItem.created_at.desc())
    
    if order_id:
        order_items = order_items.filter(OrderItem.order_id == order_id)
    elif id:
        order_items = order_items.filter(OrderItem.id == id)
    
    total_items = order_items.count() 
    offset = (page - 1) * limit
    paginated_items = order_items.offset(offset).limit(limit).all()
    
    result = []
    for item in paginated_items:
        result.append({
            "id": item.id,
            "order_id": item.order_id,
            "product_id": item.product_id,
            "product_name": item.product_name,
            "qty": item.qty,
            "price": item.price,
            "created_at": item.created_at,
        })
    
    return {
        "search_result": result,
        "items_count": total_items,
        "page": page,
        "limit": limit,
        "total_pages": (total_items + limit - 1) // limit
    }

@order_items_router.get("/order_items/{item_id}")
def get_order_item_by_id(
    item_id: str, 
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    """Lấy chi tiết 1 order item"""
    item = db.query(OrderItem).filter(OrderItem.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )
    
    return {
        "id": item.id,
        "order_id": item.order_id,
        "product_id": item.product_id,
        "product_name": item.product_name,
        "qty": item.qty,
        "price": item.price
    }

@order_items_router.get("/orders/{order_id}/items")
def get_items_by_order(
    order_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    """Lấy tất cả items của 1 order"""
    
    order = db.query(OrderBase).filter(OrderBase.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    
    result = []
    total = 0
    
    for item in items:
        item_total = item.qty * item.price
        total += item_total
        
        result.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product_name,
            "qty": item.qty,
            "price": item.price,
            "subtotal": item_total
        })
    
    return {
        "order_id": order_id,
        "items": result,
        "total_items": len(result),
        "total_amount": total
    }

@order_items_router.delete("/order_items/{item_id}")
def delete_order_item(
    item_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    """Xóa 1 order item"""
    
    item = db.query(OrderItem).filter(OrderItem.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )
    
    # Lưu thông tin trước khi xóa
    order_id = item.order_id
    
    db.delete(item)
    db.commit()
    
    return {
        "message": "Order item deleted successfully",
        "deleted_item_id": item_id,
        "order_id": order_id
    }

@order_items_router.delete("/orders/{order_id}/items")
def delete_all_items_in_order(
    order_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    """Xóa tất cả items của 1 order"""
    
    # Kiểm tra order tồn tại
    order = db.query(OrderBase).filter(OrderBase.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Đếm số lượng items
    items_count = db.query(OrderItem).filter(OrderItem.order_id == order_id).count()
    
    if items_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No items found in this order"
        )
    
    # Xóa tất cả items
    db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
    db.commit()
    
    return {
        "message": "All order items deleted successfully",
        "order_id": order_id,
        "deleted_count": items_count
    }