from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.api.deps import get_current_user
from app.core.security import create_access_token, create_refresh_token, decode_access_token
from app.db.session import get_db
from app.schemas.user import Token, UserCreate, User, TokenRefresh
from app.crud.crud_user import CRUDUser
from app.db.models.user import User as UserModel

router = APIRouter()


@router.post("/token", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    user = await CRUDUser().authenticate(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password"
        )
    return {
        "access_token": create_access_token({"sub": user.username}),
        "refresh_token": create_refresh_token({"sub": user.username}),
        "token_type": "bearer"
    }


@router.post("/token/refresh", response_model=Token)
def refresh_access_token(refresh_token: TokenRefresh):
    payload = decode_access_token(refresh_token.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token.refresh_token}


@router.post("/register", response_model=User)
async def register(
        user_in: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    user = await CRUDUser().get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = await CRUDUser().create(db, obj_in=user_in)
    return user


@router.post("/token/verify")
def verify_access_token(token: TokenRefresh):
    payload = decode_access_token(token.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return JSONResponse(
        status_code=200,
        content={"token_valid": True},
    )


@router.get("/users/me", response_model=User)
def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return current_user
