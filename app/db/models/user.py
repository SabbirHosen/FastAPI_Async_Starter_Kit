from sqlalchemy import Column, String, Integer
from app.db.base_class import Base
from app.db.base import Model


class User(Base, Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    first_name = Column(String(255), index=True)
    last_name = Column(String(255), index=True)
    email = Column(String(255), index=True)
    hashed_password = Column(String(255))
    role = Column(String(50), default="user", index=True)  # Added for RBAC