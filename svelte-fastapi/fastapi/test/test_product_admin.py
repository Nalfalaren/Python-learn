import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, engine
from main import app
from auth import require_admin
from apis.product.router_admin import get_db
TEST_DB_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override get_db
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override require_admin → Luôn pass
def override_require_admin():
    return {"role": "ADMIN"}


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides = {}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_admin] = override_require_admin

    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)

sample_product = {
    "product_name": "Test Drone",
    "category": "Drone",
    "description": "Testing drone product",
    "rating": 4.5,
    "price": 999.99,
    "stock": 10
}


def test_create_product(client):
    resp = client.post("/admin/products", json=sample_product)
    assert resp.status_code == 200
    assert resp.json()["message"] == "Product created successfully"


def test_list_products(client):
    resp = client.get("/admin/products")
    assert resp.status_code == 200
    assert "products" in resp.json() or isinstance(resp.json(), dict)


def extract_first_id(resp_json):
    if isinstance(resp_json, list):
        return resp_json[0]["id"]

    for key, value in resp_json.items():
        if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
            return value[0]["id"]

    raise ValueError("Không tìm thấy list sản phẩm trong response")


def test_update_product(client):
    list_resp = client.get("/admin/products")
    first_id = extract_first_id(list_resp.json())

    update_data = {
        "product_name": "Drone Fixed-wing",
        "category": "Fixed-wing",
        "description": "...",
        "price": 6000,
        "rating": "5.00",
        "stock": 6
    }
    resp = client.put(f"/admin/products/{first_id}", json=update_data)

    assert resp.status_code == 200
    assert resp.json()["message"] == "Product updated successfully"


def test_delete_product(client):
    list_resp = client.get("/admin/products")
    first_id = extract_first_id(list_resp.json())

    resp = client.delete(f"/admin/products/{first_id}")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Product deleted successfully"

    resp = client.delete(f"/admin/products/{first_id}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Product not found"


