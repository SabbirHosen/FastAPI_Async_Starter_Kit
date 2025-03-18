from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    model_config = ConfigDict(from_attributes=True, extra='ignore')
    id: int


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenRefresh(BaseModel):
    refresh_token: str
