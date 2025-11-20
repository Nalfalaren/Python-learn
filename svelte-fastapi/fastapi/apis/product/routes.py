import base64
import json
import logging
from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from auth import get_current_user
from role import StatusCode
from .models import ProductBase
from .schema import ProductSchema, ProductUpdatePropsSchema, SuccessMessageSchema
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter(tags=['Products'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/me")
def get_account(current_user: dict = Depends(get_current_user)):
    return current_user

@router.get('/products')
def get_products_list(db: Session = Depends(get_db), account_info: dict = Depends(get_account), search_id: str | None = Query(None, description="Search by ID"), search_product: str | None = Query(None, description="Search by Employee Name"), next_cursor: str | None = Query(None, description="Pagination cursor"), limit: int = Query(10, description="Limit")):
    account_role = account_info.get("role")
    if(account_role != 'admin'):
        raise HTTPException(
            status_code=StatusCode.HTTP_FORBIDDEN_403.value,
            detail="You are not allowed to access this data!",
        )
    
    decoded_cursor = None
    if next_cursor:
        try:
            decoded_json = base64.b64decode(next_cursor).decode("utf-8")
            decoded_cursor = json.loads(decoded_json)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid cursor: {str(e)}")
    
    products = db.query(ProductBase)

    if(search_id):
        products = products.filter(ProductBase.id.contains(search_id))
    elif(search_product):
        products = products.filter(ProductBase.product_name.contains(search_product))

    if decoded_cursor:
        last_date = decoded_cursor.get("date")
        last_id = decoded_cursor.get("id")

        # Only add this if both exist
        if last_date and last_id:
            products = products.filter(
                (ProductBase.created_at < last_date)
                | ((ProductBase.created_at == last_date) & (ProductBase.id < last_id))
            )

    # Sort newest first
    products = products.order_by(ProductBase.created_at.desc(), ProductBase.id.desc())
    products = products.limit(limit).all()


    next_cursor_value = None
    if products:
        last = products[-1]
        next_cursor_obj = {
            "date": last.created_at.isoformat() if last.created_at else None,
            "id": last.id,
        }
        encoded_cursor = base64.b64encode(
            json.dumps(next_cursor_obj).encode("utf-8")
        ).decode("utf-8")
        next_cursor_value = encoded_cursor
    
    total_products = db.query(ProductBase).count()
    return {
        "message": "Search successfully",
        "search_result": products,
        "employee_count": len(products),
        "total_employee": total_products,
        "next_cursor": next_cursor_value,
    }

@router.post("/products", response_model=SuccessMessageSchema)
def create_product(
    product_info: ProductSchema,
    db: Session = Depends(get_db),
    account_info: dict = Depends(get_account),
):
    user_role = account_info.get('role')
    if user_role != 'admin':
        raise HTTPException(
            status_code=StatusCode.HTTP_FORBIDDEN_403.value,
            detail='You cannot access this page!'
        )

    new_product = ProductBase(
        id=str(uuid.uuid4()),
        product_name=product_info.product_name,
        category=product_info.category,
        price=product_info.price,
        is_active=product_info.is_active,
        created_at= datetime.utcnow(),
        updated_at = datetime.utcnow()
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return SuccessMessageSchema(message='Product created successfully')

@router.put('/products/{product_id}', response_model=SuccessMessageSchema)
def update_product(product: ProductUpdatePropsSchema, product_id: str, db: Session = Depends(get_db)):
    product_update = db.query(ProductBase).filter(ProductBase.id == product_id).first()
    if not product_update:
        raise HTTPException(status_code=StatusCode.HTTP_ERROR_404, detail='Product not found')
      # Update giá trị vào SQLAlchemy model
    for key, value in product.dict(exclude_unset=True).items():
        setattr(product_update, key, value)
    
    db.commit()   # lưu vào DB
    db.refresh(product_update)  # cập nhật lại object nếu cần

    return SuccessMessageSchema(message='Product updated successfully')

@router.get('/products/{product_id}', response_model=ProductSchema)
def get_product_detail(product_id: str, db: Session = Depends(get_db)):
    if not product_id:
        raise HTTPException(status_code=StatusCode.HTTP_ERROR_404, detail='Product not found')
    product = db.query(ProductBase).where(ProductBase.id == product_id)
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')
    return product



    