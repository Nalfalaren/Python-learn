from fastapi import FastAPI
from apis.employee.routes import router as employee_router
from apis.login.routes import router as register_router
from apis.product.router_client import router_client as product_router_client
from apis.product.router_admin import router_admin as product_router_admin
from apis.orders.routes import order_router
from apis.orders_item.routes import order_items_router as order_items_router
from apis.customer.routes import router as customer_router
from database import Base, engine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Company API")
origins = ['http://localhost:5173', 'https://python-learn-d3pj.vercel.app']
    
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

app.include_router(employee_router)
app.include_router(customer_router)
app.include_router(register_router)
app.include_router(product_router_client)
app.include_router(product_router_admin)
app.include_router(order_router)
app.include_router(order_items_router)

Base.metadata.create_all(bind=engine)