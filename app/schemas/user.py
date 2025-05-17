from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    role: str = "user"  # Added for RBAC


class UserCreate(UserBase):
    password: str
    role: str = "user"  # Added for RBAC


class User(UserBase):
    model_config = ConfigDict(from_attributes=True, extra='ignore')
    id: int
    role: str = "user"  # Added for RBAC


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenRefresh(BaseModel):
    refresh_token: str
