from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware

from .auth import verify_token


class AdminAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/admin"):
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return JSONResponse({"detail": "Unauthorized"}, status_code=401)

            token = authorization.split(" ", 1)[1]
            try:
                payload = verify_token(token)
            except HTTPException as exc:
                return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
            except JWTError as exc:
                return JSONResponse({"detail": "Token inválido"}, status_code=401)

            request.state.admin = payload
        return await call_next(request)