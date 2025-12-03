from fastapi import FastAPI
from middleware import AuthMiddleware
from .routes_employee import router_employee as forget_password_employee_route
from .routes_customer import router_customer as forget_password_customer_route
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='Demo employee', version='1.0')
app.include_router(forget_password_employee_route)
app.include_router(forget_password_customer_route)
app.add_middleware(AuthMiddleware)

origins = ['http://localhost:5173', 'https://python-learn-d3pj.vercel.app']
    
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app = FastAPI()



    
