import os
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError, jwt

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_paths = ["/login", "/signup", "/docs", "/openapi.json"]
        if request.url.path in public_paths:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(status_code=401, content={"message": "Missing Authorization header"})

        token = auth_header.replace("Bearer ", "")
        try:
            jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        except jwt.ExpiredSignatureError:
            return JSONResponse(status_code=401, content={"message": "Token expired"})
        except JWTError:
            return JSONResponse(status_code=401, content={"message": "Invalid token"})

        return await call_next(request)
