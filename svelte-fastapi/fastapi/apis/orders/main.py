from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from middleware import AuthMiddleware
import logging
from .routes import router as order_router

# Cấu hình logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title='Demo products', version='1.0')
app.include_router(order_router)
origins = ['http://localhost:5173']

app.add_middleware(AuthMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

if __name__ == '__main__':
    uvicorn.run('main:app', port=8080, reload=True)
