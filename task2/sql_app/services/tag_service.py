"""
Tag and Task Assignment CRUD services.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sql_app.models import Tag, TaskAssignment, Task
from sql_app.schemas import TagCreate, TagUpdate, TaskAssignmentCreate
from sql_app.services.base import BaseCRUDService


class TagService(BaseCRUDService[Tag, TagCreate, TagUpdate]):
    """Tag CRUD service."""

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Tag]:
        """Get tag by name."""
        query = select(Tag).where(Tag.name == name)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_tag_with_tasks(self, db: AsyncSession, id: UUID) -> Optional[Tag]:
        """Get tag with associated tasks."""
        query = select(Tag).where(Tag.id == id).options(selectinload(Tag.tasks))
        result = await db.execute(query)
        return result.scalars().first()

    async def attach_to_task(
        self, db: AsyncSession, tag_id: UUID, task_id: UUID
    ) -> bool:
        """Attach tag to task."""
        tag = await self.get(db, tag_id)
        task = await db.get(Task, task_id)

        if tag and task:
            task.tags.append(tag)
            db.add(task)
            await db.commit()
            return True
        return False

    async def detach_from_task(
        self, db: AsyncSession, tag_id: UUID, task_id: UUID
    ) -> bool:
        """Detach tag from task."""
        task = await db.get(Task, task_id)
        if task:
            task.tags = [t for t in task.tags if t.id != tag_id]
            db.add(task)
            await db.commit()
            return True
        return False


class TaskAssignmentService(BaseCRUDService[TaskAssignment, TaskAssignmentCreate, TaskAssignmentCreate]):
    """Task Assignment CRUD service."""

    async def get_task_assignments(self, db: AsyncSession, task_id: UUID) -> list[TaskAssignment]:
        """Get all assignments for a task."""
        query = (
            select(TaskAssignment)
            .where(TaskAssignment.task_id == task_id)
            .options(selectinload(TaskAssignment.user), selectinload(TaskAssignment.task))
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_user_assignments(self, db: AsyncSession, user_id: UUID) -> list[TaskAssignment]:
        """Get all assignments for a user."""
        query = (
            select(TaskAssignment)
            .where(TaskAssignment.user_id == user_id)
            .options(selectinload(TaskAssignment.task), selectinload(TaskAssignment.user))
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def remove_assignment(self, db: AsyncSession, task_id: UUID, user_id: UUID) -> bool:
        """Remove assignment."""
        query = select(TaskAssignment).where(
            (TaskAssignment.task_id == task_id) & (TaskAssignment.user_id == user_id)
        )
        result = await db.execute(query)
        assignment = result.scalars().first()

        if assignment:
            await db.delete(assignment)
            await db.commit()
            return True
        return False


tag_service = TagService(Tag)
task_assignment_service = TaskAssignmentService(TaskAssignment)
