from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.custom_exception import CustomException
from app.core.config import settings
from app.api.v1 import auth
from fastapi.responses import FileResponse
import os

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Smart Valuation", description="Async FastAPI Starter Kit with JWT, Alembic, SQLAlchemy, Email, Logging, Rate Limiting, and more.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/", response_class=FileResponse, include_in_schema=False)
async def read_root():
    return FileResponse(os.path.join("app/api/templates", "index.html"))

@app.get("/health", tags=["Health"], summary="Health Check", description="Returns API health status.")
async def health_check():
    return {"status": "healthy"}

app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])

@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc: CustomException):
    return JSONResponse(
        status_code=exc.error_code,
        content={"error": {"name": exc.name, "detail": exc.detail}},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)


@app.exception_handler(ResponseValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)
