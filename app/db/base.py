from sqlalchemy import asc, desc, JSON, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.logger import logger


class Model:
    @classmethod
    async def get_all_objects(cls, db: AsyncSession, order_by: list = None, **kwargs):
        try:
            query = select(cls)

            # Apply filtering with JSON handling
            for key, value in kwargs.items():
                if hasattr(cls, key) and isinstance(getattr(cls, key).type, JSON):
                    continue
                else:
                    query = query.where(getattr(cls, key) == value)

            # Apply ordering if provided
            if order_by:
                for field, ascending in order_by:
                    query = query.order_by(asc(field) if ascending else desc(field))

            result = await db.execute(query)
            return result.scalars().all()
        except Exception as ex:
            logger.error(f"Error encountered while getting all objects: {str(ex)}")
            raise

    @classmethod
    async def get_single_object(cls, db: AsyncSession, **kwargs):
        try:
            query = select(cls)

            # Apply filtering with JSON handling
            for key, value in kwargs.items():
                if hasattr(cls, key) and isinstance(getattr(cls, key).type, JSON):
                    continue
                else:
                    query = query.where(getattr(cls, key) == value)

            result = await db.execute(query)
            return result.scalars().first()
        except Exception as ex:
            logger.error(f"Error encountered while getting single object: {str(ex)}")
            raise

    @classmethod
    async def get_objects_by_pagination(cls, db: AsyncSession, page=1, per_page=10, order_by: list = None, **kwargs):
        try:
            query = select(cls)

            # Apply filtering with JSON handling
            for key, value in kwargs.items():
                if hasattr(cls, key) and isinstance(getattr(cls, key).type, JSON):
                    continue
                else:
                    query = query.where(getattr(cls, key) == value)

            # Apply ordering if provided
            if order_by:
                for field, ascending in order_by:
                    query = query.order_by(asc(field) if ascending else desc(field))

            # Apply pagination
            query = query.limit(per_page).offset((page - 1) * per_page)
            result = await db.execute(query)
            items = result.scalars().all()

            # Get total count
            count_query = select(func.count()).select_from(cls)
            count_result = await db.execute(count_query)
            count = count_result.scalar_one()

            return items, count
        except Exception as ex:
            logger.error(f"Error encountered while getting objects by pagination: {str(ex)}")
            raise

    @classmethod
    async def exists(cls, db: AsyncSession, **kwargs) -> bool:
        try:
            query = select(cls).filter_by(**kwargs)
            result = await db.execute(query)
            return result.scalars().first() is not None
        except Exception as ex:
            logger.error(f"Error encountered while checking existence: {str(ex)}")
            raise

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs):
        try:
            valid_kwargs = {key: value for key, value in kwargs.items() if hasattr(cls, key)}
            obj = cls(**valid_kwargs)
            db.add(obj)
            await db.commit()
            await db.refresh(obj)
            return obj
        except Exception as ex:
            await db.rollback()
            logger.error(f"Error encountered while creating object: {str(ex)}")
            raise

    @classmethod
    async def update(cls, id, db: AsyncSession, **kwargs):
        try:
            query = select(cls).filter_by(id=id)
            result = await db.execute(query)
            obj = result.scalars().first()
            if not obj:
                raise Exception("Object not found")
            for key, value in kwargs.items():
                setattr(obj, key, value)
            await db.commit()
            await db.refresh(obj)
            return obj
        except Exception as ex:
            await db.rollback()
            logger.error(f"Error encountered while updating object: {str(ex)}")
            raise

    @classmethod
    async def delete(cls, id, db: AsyncSession):
        try:
            query = select(cls).filter_by(id=id)
            result = await db.execute(query)
            obj = result.scalars().first()
            if not obj:
                raise Exception("Object not found")
            await db.delete(obj)
            await db.commit()
        except Exception as ex:
            await db.rollback()
            logger.error(f"Error encountered while deleting object: {str(ex)}")
            raise
