from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from .service import get_products_list
from .repository import get_product_by_id

router_client = APIRouter(tags=["Client Products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router_client.get("/products")
def list_products(
    db: Session = Depends(get_db),
    search_id: str | None = Query(None),
    search_product: str | None = Query(None),
    next_cursor: str | None = Query(None),
    limit: int = Query(10),
    category: str | None = Query("All"),
    sort_by: str | None = Query("featured"),
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

@router_client.get("/products/{product_id}")
def get_product_detail(product_id: str, db: Session = Depends(get_db)):
    product_obj = get_product_by_id(db, product_id)
    if not product_obj:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_obj


