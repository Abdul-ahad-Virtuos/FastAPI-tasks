"""
User CRUD service.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sql_app.models import User
from sql_app.schemas import UserCreate, UserUpdate
from sql_app.services.base import BaseCRUDService


class UserService(BaseCRUDService[User, UserCreate, UserUpdate]):
    """User CRUD service."""

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username."""
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_active_users(self, db: AsyncSession) -> list[User]:
        """Get all active users."""
        query = select(User).where(User.is_active == True)
        result = await db.execute(query)
        return result.scalars().all()

    async def deactivate(self, db: AsyncSession, id: UUID) -> Optional[User]:
        """Deactivate a user."""
        user = await self.get(db, id)
        if user:
            user.is_active = False
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user


user_service = UserService(User)
