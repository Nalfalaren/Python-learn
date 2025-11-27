from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .service import get_products_list
from .repository import get_product_by_id
from .schema import ProductSchema, ProductUpdatePropsSchema, SuccessMessageSchema
from database import SessionLocal
from auth import get_current_user
from role import StatusCode
import uuid
from datetime import datetime
from .models import ProductBase

router_admin = APIRouter(tags=["Admin Products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router_admin.post("/products", response_model=SuccessMessageSchema)
def create_product(
    product_info: ProductSchema,
    db: Session = Depends(get_db),
    account_info: dict = Depends(get_current_user),
):
    if account_info.get("role") != "admin":
        raise HTTPException(
            status_code=StatusCode.HTTP_FORBIDDEN_403.value,
            detail="You cannot access this page!",
        )

    new_product = ProductBase(
        id=str(uuid.uuid4()),
        product_name=product_info.product_name,
        category=product_info.category,
        price=product_info.price,
        is_active=product_info.is_active,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return SuccessMessageSchema(message="Product created successfully")

@router_admin.put("/products/{product_id}", response_model=SuccessMessageSchema)
def update_product(product_id: str, product: ProductUpdatePropsSchema, db: Session = Depends(get_db)):
    product_obj = get_product_by_id(db, product_id)
    if not product_obj:
        raise HTTPException(status_code=404, detail="Product not found")
    for k, v in product.dict(exclude_unset=True).items():
        setattr(product_obj, k, v)
    product_obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product_obj)
    return SuccessMessageSchema(message="Product updated successfully")

@router_admin.delete("/products/{product_id}", response_model=SuccessMessageSchema)
def delete_product(product_id: str, db: Session = Depends(get_db)):
    product_obj = get_product_by_id(db, product_id)
    if not product_obj:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product_obj)
    db.commit()
    return SuccessMessageSchema(message="Product deleted successfully")
