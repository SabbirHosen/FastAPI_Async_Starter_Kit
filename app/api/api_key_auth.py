from fastapi import Header, HTTPException, status, Security
from fastapi.security.api_key import APIKeyHeader
import os

API_KEY = os.getenv("API_KEY", "supersecretkey")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
    return api_key
