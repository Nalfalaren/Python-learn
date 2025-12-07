from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .service import get_products_list
from .repository import get_product_by_id
from .schema import ProductSchema, ProductUpdatePropsSchema, SuccessMessageSchema
from database import SessionLocal
from auth import require_admin
import uuid
from datetime import datetime
from .models import ProductBase
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

router_admin = APIRouter(prefix="/admin", tags=["Admin Products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router_admin.get("/products")
def list_products(
    db: Session = Depends(get_db),
    search_id: str | None = Query(None),
    search_product: str | None = Query(None),
    next_cursor: str | None = Query(None),
    limit: int = Query(10),
    category: str | None = Query("All"),
    sort_by: str | None = Query("featured"),
    _: dict = Depends(require_admin)
):
    return get_products_list(
        db=db,
        search_id=search_id,
        search_product=search_product,
        next_cursor=next_cursor,
        limit=limit,
        category=category,
        sort_by=sort_by,
    )

@router_admin.post("/products", response_model=SuccessMessageSchema)
def create_product(
    product_info: ProductSchema,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    new_product = ProductBase(
        id=str(uuid.uuid4()),
        product_name=product_info.product_name,
        category=product_info.category,
        description=product_info.description,
        rating=product_info.rating,
        price=product_info.price,
        stock=product_info.stock,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return SuccessMessageSchema(message="Product created successfully")

@router_admin.put("/products/{product_id}", response_model=SuccessMessageSchema)
def update_product(product_id: str, product: ProductUpdatePropsSchema, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    product_obj = get_product_by_id(db, product_id)
    if not product_obj:
        raise HTTPException(status_code=404, detail="Product not found")
    for k, v in product.dict(exclude_unset=True).items():
        setattr(product_obj, k, v)
    product_obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product_obj)
    return {"message" :  "Product updated successfully"}

@router_admin.delete("/products/{product_id}", response_model=SuccessMessageSchema)
def delete_product(product_id: str, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    try:
        product_obj = get_product_by_id(db, product_id)

        if not product_obj:
            raise HTTPException(status_code=404, detail="Product not found")

        db.delete(product_obj)
        db.commit()

        return {"message": "Product deleted successfully"}

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete product because it is referenced in orders."
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error while deleting product"
        )

