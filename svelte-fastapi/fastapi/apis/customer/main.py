from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from auth import get_current_user
from middleware import AuthMiddleware
import logging
from .routes import router as customer_router

# Cấu hình logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title='Demo employee', version='1.0')
app.include_router(customer_router)

origins = ['http://localhost:5173', 'https://python-learn-d3pj.vercel.app']

app.add_middleware(AuthMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.get("/me")
def get_account(current_user: dict = Depends(get_current_user)):
    return current_user
    
if __name__ == '__main__':
    uvicorn.run('main:app', port=8080, reload=True)



