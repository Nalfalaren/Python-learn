import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid
from main import app
from database import Base, engine, SessionLocal
from apis.product.models import ProductBase
from apis.orders.models import OrderBase
from apis.orders_item.models import OrderItem

# --- Fixtures ---
@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    session: Session = SessionLocal()
    yield session
    session.rollback()
    session.close()


# --- Seed data helper ---
def seed_product(session: Session):
    product = ProductBase(
        id=str(uuid.uuid4()),
        product_name="Test Product",
        category="Category1",
        description="Desc",
        rating=5,
        price=100,
        stock=10
    )
    session.add(product)
    session.commit()
    return product


def seed_order(session: Session):
    order = OrderBase(
        id=str(uuid.uuid4()),
        customer_name="John Doe",
        email="john@example.com",
        phone="123",
        address="Address",
        status="PENDING"
    )
    session.add(order)
    session.commit()
    return order

# --- Tests ---
def test_checkout_success(client, db_session):
    product = seed_product(db_session)
    payload = {
        "customer": {"customer_id": "1234", "name": "John Doe", "email": "john@example.com", "phone": "123", "address": "Address"},
        "cart": [{"product_id": product.id, "product_name": product.product_name, "qty": 2, "price": product.price}]
    }
    res = client.post("/checkout", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "order_id" in data

    db = SessionLocal()
    p = db.query(ProductBase).filter(ProductBase.id == product.id).first()
    assert p.stock == 8  # 10 - 2
    db.close()


def test_checkout_fail_insufficient_stock(client, db_session):
    product = seed_product(db_session)
    payload = {
        "customer": {"customer_id": "1234", "name": "Jane", "email": "jane@example.com", "phone": "456", "address": "Address"},
        "cart": [{"product_id": product.id, "product_name": product.product_name, "qty": 20, "price": product.price}]
    }
    res = client.post("/checkout", json=payload)
    assert res.status_code == 400
    assert "chỉ còn" in res.json()["detail"]


def test_get_order_items(client, db_session):
    order = seed_order(db_session)
    db_session.add(OrderItem(
        id="item1", order_id=order.id, product_id="prod1",
        product_name="Test Product", qty=1, price=100
    ))
    db_session.commit()

    res = client.get(f"/order_items?order_id={order.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["items_count"] == 1


def test_delete_order_item(client, db_session):
    order = seed_order(db_session)
    item = OrderItem(
        id="item2", order_id=order.id, product_id="prod1",
        product_name="Test Product", qty=1, price=100
    )
    db_session.add(item)
    db_session.commit()

    res = client.delete(f"/order_items/{item.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["deleted_item_id"] == item.id

    db = SessionLocal()
    deleted = db.query(OrderItem).filter(OrderItem.id == item.id).first()
    assert deleted is None
    db.close()

    db = SessionLocal()
    remaining = db.query(OrderItem).filter(OrderItem.order_id == order.id).count()
    assert remaining == 0
    db.close()
