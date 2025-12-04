from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base
from apis.orders.models import OrderBase
from apis.orders_item.models import OrderItem
from apis.product.models import ProductBase
from apis.login.models import AccountBase
from auth import get_current_user, require_admin, require_employee
from datetime import datetime

TEST_DB = "sqlite:///./test_orders.db"

engine = create_engine(
    TEST_DB, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


# -------------------------------
# Override dependencies
# -------------------------------
def override_employee():
    return {"id": "emp1", "role": "EMPLOYEE"}

def override_admin():
    return {"id": "adm1", "role": "ADMIN"}

def override_user():
    return {"id": "u1", "role": "EMPLOYEE"}

app.dependency_overrides[require_employee] = override_employee
app.dependency_overrides[require_admin] = override_admin
app.dependency_overrides[get_current_user] = override_user

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


from apis.orders.routes import get_db as order_get_db
app.dependency_overrides[order_get_db] = override_get_db

client = TestClient(app)

def create_seed_order():
    db = TestingSessionLocal()

    product = ProductBase(
        id="p1", product_name="Product 1", category="A",
        description="Test", rating=4.5, price=50, stock=100
    )
    db.add(product)

    order = OrderBase(
        id="o1",
        customer_name="John Doe",
        email="john@example.com",
        phone="123",
        address="HN",
        status="PENDING"
    )
    db.add(order)
    db.commit()

    item = OrderItem(
        id="i1",
        order_id="o1",
        product_id="p1",
        product_name="Product 1",
        qty=2,
        price=50,
        created_at=datetime.utcnow()
    )
    db.add(item)
    db.commit()

    db.close()


# ============================================================
# TEST CASES
# ============================================================

def test_get_orders_empty():
    res = client.get("/orders")
    assert res.status_code == 200
    assert res.json()["orders_count"] == 0


def test_get_orders_list():
    create_seed_order()

    res = client.get("/orders")
    assert res.status_code == 200

    data = res.json()
    assert data["orders_count"] == 1
    assert data["search_result"][0]["id"] == "o1"


def test_get_order_detail_success():
    res = client.get("/orders/o1")

    assert res.status_code == 200
    assert res.json()["order"]["id"] == "o1"
    assert len(res.json()["items"]) == 1


def test_get_order_detail_not_found():
    res = client.get("/orders/unknown")
    assert res.status_code == 404


def test_update_order_cancelled_updates_stock():
   res = client.put(
    "/orders/o1",
    json={
        "status": "CANCELLED",
        "customer_name": "ABC",
        "email": "a@gmail.com",
        "phone": "02932873238",
        "address": "test"
    }
)
   
   assert res.status_code == 200
   db = TestingSessionLocal()
   product = db.query(ProductBase).filter(ProductBase.id == "p1").first()
   assert product.stock == 102
   db.close()


def test_delete_order_success():
    res = client.delete("/orders/o1")
    assert res.status_code == 200
    assert res.json()["message"] == "Delete order successfully"

    # Confirm deleted
    db = TestingSessionLocal()
    order = db.query(OrderBase).filter(OrderBase.id == "o1").first()
    assert order is None
    db.close()


def test_delete_order_not_found():
    res = client.delete("/orders/nonexistent")
    assert res.status_code == 404


def test_assign_order_success():
    db = TestingSessionLocal()

    # Seed new order + employee
    order = OrderBase(
        id="o2",
        customer_name="Alice",
        email="alice@example.com",
        phone="456",
        address="HN",
        status="PENDING"
    )
    db.add(order)
    employee = AccountBase(
        id="emp2",
        employee_name="Bob",
        email="bob@example.com",
        password="hashed",
        role="EMPLOYEE"
    )
    db.add(employee)
    db.commit()
    db.close()

    res = client.post("/orders/o2/assign", json={"order_id": "o2", "employee_id": "emp2"})
    assert res.status_code == 200
    data = res.json()
    assert data["employee_id"] == "emp2"
    assert data["status"] == "ASSIGNED"
    assert data["assigned_to"] == "Bob"


def test_assign_order_fail_non_employee():
    db = TestingSessionLocal()
    # Seed admin account
    admin = AccountBase(
        id="admin1",
        employee_name="Admin",
        email="admin@example.com",
        password="hashed",
        role="ADMIN"
    )
    db.add(admin)
    db.commit()
    db.close()

    res = client.post("/orders/o2/assign", json={"order_id": "o2", "employee_id": "admin1"})
    assert res.status_code == 400
    assert "Only employees" in res.json()["detail"]
