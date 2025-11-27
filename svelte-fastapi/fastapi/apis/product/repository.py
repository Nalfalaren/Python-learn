from sqlalchemy.orm import Session
from .models import ProductBase

def get_products_query(db: Session):
    return db.query(ProductBase)

def get_product_by_id(db: Session, product_id: str):
    return db.query(ProductBase).filter(ProductBase.id == product_id).first()
