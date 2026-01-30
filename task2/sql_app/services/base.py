"""
Base CRUD service with common operations.
"""
from typing import TypeVar, Generic, Type, List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseCRUDService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base CRUD service with common operations."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(
        self, db: AsyncSession, obj_in: CreateSchemaType
    ) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: UUID) -> Optional[ModelType]:
        """Get a record by ID."""
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get all records with pagination."""
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def update(
        self,
        db: AsyncSession,
        id: UUID,
        obj_in: UpdateSchemaType,
    ) -> Optional[ModelType]:
        """Update a record."""
        db_obj = await self.get(db, id)
        if not db_obj:
            return None

        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: UUID) -> Optional[ModelType]:
        """Delete a record."""
        db_obj = await self.get(db, id)
        if not db_obj:
            return None

        await db.delete(db_obj)
        await db.commit()
        return db_obj

    async def count(self, db: AsyncSession) -> int:
        """Count all records."""
        query = select(func.count(self.model.id))
        result = await db.execute(query)
        return result.scalar()
