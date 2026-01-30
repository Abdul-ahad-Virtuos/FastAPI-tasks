"""
Task Comment CRUD service.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sql_app.models import TaskComment
from sql_app.schemas import TaskCommentCreate, TaskCommentUpdate
from sql_app.services.base import BaseCRUDService


class TaskCommentService(BaseCRUDService[TaskComment, TaskCommentCreate, TaskCommentUpdate]):
    """Task comment CRUD service."""

    async def get_task_comments(self, db: AsyncSession, task_id: UUID) -> list[TaskComment]:
        """Get all comments for a task."""
        query = (
            select(TaskComment)
            .where(TaskComment.task_id == task_id)
            .options(selectinload(TaskComment.created_by_user))
            .order_by(TaskComment.created_at.desc())
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_user_comments(self, db: AsyncSession, user_id: UUID) -> list[TaskComment]:
        """Get all comments created by a user."""
        query = (
            select(TaskComment)
            .where(TaskComment.created_by == user_id)
            .options(selectinload(TaskComment.task))
            .order_by(TaskComment.created_at.desc())
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_with_details(self, db: AsyncSession, id: UUID) -> Optional[TaskComment]:
        """Get comment with all details."""
        query = (
            select(TaskComment)
            .where(TaskComment.id == id)
            .options(selectinload(TaskComment.task), selectinload(TaskComment.created_by_user))
        )
        result = await db.execute(query)
        return result.scalars().first()


task_comment_service = TaskCommentService(TaskComment)
