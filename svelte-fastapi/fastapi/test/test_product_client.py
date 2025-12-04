# test/test_client_products.py
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base
from apis.product.models import ProductBase
from apis.product.router_client import get_db

# ---------------------------------
# Setup Test Database SQLite
# ---------------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_client_products.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Reset schema
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# ---------------------------------
# Override DB Dependency
# ---------------------------------
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# ---------------------------------
# Tạo sản phẩm mẫu
# ---------------------------------
def create_sample_product(id="p2", name="Product A"):
    db = TestingSessionLocal()
    product = ProductBase(
        id=id,
        product_name=name,
        category="Category1",
        description="A product",
        rating=4.5,
        price=100.0,
        stock=10,
        created_at= datetime.utcnow(),
        updated_at= datetime.utcnow(),
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    db.close()
    return product


# ---------------------------------
# TEST CASES
# ---------------------------------

def test_list_products_empty():
    res = client.get("/products")

    assert res.status_code == 200
    assert isinstance(res.json()['search_result'], list)
    assert len(res.json()['search_result']) == 0

def test_get_product_detail_success():
    create_sample_product("p2", "Product A")
    res = client.get("/products/p2")
    assert res.status_code == 200
    data = res.json()

    assert data["id"] == "p2"
    assert data["product_name"] == "Product A"


def test_get_product_detail_not_found():
    res = client.get("/products/unknown")

    assert res.status_code == 404
    assert res.json()["detail"] == "Product not found"
