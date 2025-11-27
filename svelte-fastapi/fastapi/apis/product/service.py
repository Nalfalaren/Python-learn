import base64
import json
from sqlalchemy import func
from sqlalchemy.orm import Session
from .models import ProductBase
from .repository import get_products_query

def encode_cursor(last_item):
    obj = {
        "date": last_item.created_at.isoformat() if last_item.created_at else None,
        "id": last_item.id,
    }
    return base64.b64encode(json.dumps(obj).encode("utf-8")).decode("utf-8")

def decode_cursor(next_cursor: str):
    try:
        decoded_json = base64.b64decode(next_cursor).decode("utf-8")
        return json.loads(decoded_json)
    except Exception:
        return None

def get_products_list(
    db: Session,
    search_id: str = None,
    search_product: str = None,
    next_cursor: str = None,
    limit: int = 10,
    category: str = None,
    sort_by: str = None,  # 'price-asc', 'price-desc', 'rating', 'featured'
):
    query = get_products_query(db)

    # search
    if search_id:
        query = query.filter(ProductBase.id.like(f"%{search_id}%"))
    if search_product:
        query = query.filter(func.lower(ProductBase.product_name).like(f"%{search_product.lower()}%"))
    if category and category != "All":
        query = query.filter(ProductBase.category == category)

    # cursor
    decoded_cursor = decode_cursor(next_cursor)
    if decoded_cursor:
        last_date = decoded_cursor.get("date")
        last_id = decoded_cursor.get("id")
        if last_date and last_id:
            query = query.filter(
                (ProductBase.created_at < last_date)
                | ((ProductBase.created_at == last_date) & (ProductBase.id < last_id))
            )

    # sort
    if sort_by == "price-asc":
        query = query.order_by(ProductBase.price.asc())
    elif sort_by == "price-desc":
        query = query.order_by(ProductBase.price.desc())
    elif sort_by == "rating":
        query = query.order_by(ProductBase.rating.desc())
    else:
        query = query.order_by(ProductBase.created_at.desc(), ProductBase.id.desc())

    items = query.limit(limit).all()
    next_cursor_value = encode_cursor(items[-1]) if items else None
    total_count = db.query(ProductBase).count()

    return {
        "search_result": items,
        "next_cursor": next_cursor_value,
        "product_count": len(items),
        "total_product": total_count,
    }
