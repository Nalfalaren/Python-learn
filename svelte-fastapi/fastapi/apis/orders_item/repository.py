from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .models import OrderItem
from auth import get_current_user
def get_order_items_query(db: Session):
    return db.query(OrderItem)

def get_order_items_by_id(db: Session, order_id: str):
    return db.query(OrderItem).filter(OrderItem.id == order_id).first()

def get_account_role(account_info: dict = Depends(get_current_user)):
    account_role = account_info.get("role")
    return account_role