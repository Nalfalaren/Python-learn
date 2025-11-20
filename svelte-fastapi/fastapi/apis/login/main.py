from fastapi import FastAPI
from middleware import AuthMiddleware
from .routes import router as register_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='Demo employee', version='1.0')
app.include_router(register_router, prefix="/auth")
app.add_middleware(AuthMiddleware)

origins = ['http://localhost:5173']
    
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app = FastAPI()



    
