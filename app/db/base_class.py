from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

# Define the base class for models
class Base(AsyncAttrs, DeclarativeBase):
    pass

# Create the asynchronous engine
engine = create_async_engine(settings.get_database_url, echo=True)

# Create the asynchronous session maker
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
