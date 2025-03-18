from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.schemas.user import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CRUDUser:
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: UserCreate) -> User:
        hashed_password = pwd_context.hash(obj_in.password)
        db_user = User(
            username=obj_in.username,
            hashed_password=hashed_password,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            email=obj_in.email,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def authenticate(
        self, db: AsyncSession, *, username: str, password: str
    ) -> Optional[User]:
        user = await self.get_by_username(db, username=username)
        if not user:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user

crud_user = CRUDUser()