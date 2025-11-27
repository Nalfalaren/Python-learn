from sqlalchemy.orm import Session
from .models import OrderBase

def get_orders_query(db: Session):
    return db.query(OrderBase)

def get_order_by_id(db: Session, customer_id: str):
    return db.query(OrderBase).filter(OrderBase.id == customer_id).first()
