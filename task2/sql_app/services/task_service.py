"""
Task CRUD service.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sql_app.models import Task, TaskStatus, TaskPriority
from sql_app.schemas import TaskCreate, TaskUpdate
from sql_app.services.base import BaseCRUDService


class TaskService(BaseCRUDService[Task, TaskCreate, TaskUpdate]):
    """Task CRUD service."""

    async def get_with_relations(self, db: AsyncSession, id: UUID) -> Optional[Task]:
        """Get task with all relations."""
        query = (
            select(Task)
            .where(Task.id == id)
            .options(
                selectinload(Task.project),
                selectinload(Task.assigned_to_user),
                selectinload(Task.tags),
                selectinload(Task.assignments),
                selectinload(Task.comments),
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_project(self, db: AsyncSession, project_id: UUID) -> list[Task]:
        """Get all tasks in a project."""
        query = (
            select(Task)
            .where(Task.project_id == project_id)
            .options(selectinload(Task.assigned_to_user), selectinload(Task.tags))
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_status(
        self, db: AsyncSession, status: TaskStatus
    ) -> list[Task]:
        """Get all tasks with a specific status."""
        query = (
            select(Task)
            .where(Task.status == status)
            .options(selectinload(Task.assigned_to_user))
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_assignee(self, db: AsyncSession, user_id: UUID) -> list[Task]:
        """Get all tasks assigned to a user."""
        query = (
            select(Task)
            .where(Task.assigned_to == user_id)
            .options(selectinload(Task.project), selectinload(Task.tags))
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_overdue_tasks(self, db: AsyncSession) -> list[Task]:
        """Get all overdue tasks."""
        now = datetime.now(datetime.now().astimezone().tzinfo)
        query = (
            select(Task)
            .where(
                and_(
                    Task.due_date < now,
                    Task.status != TaskStatus.COMPLETED,
                    Task.status != TaskStatus.CANCELLED,
                )
            )
            .options(selectinload(Task.assigned_to_user), selectinload(Task.project))
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_upcoming_tasks(
        self, db: AsyncSession, days: int = 7
    ) -> list[Task]:
        """Get upcoming tasks due within specified days."""
        now = datetime.now(datetime.now().astimezone().tzinfo)
        future = datetime.fromtimestamp(
            (now.timestamp() + (days * 86400))
        ).replace(tzinfo=now.tzinfo)

        query = (
            select(Task)
            .where(
                and_(
                    Task.due_date.between(now, future),
                    Task.status != TaskStatus.COMPLETED,
                )
            )
            .options(selectinload(Task.assigned_to_user), selectinload(Task.project))
            .order_by(Task.due_date)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_priority(
        self, db: AsyncSession, priority: TaskPriority
    ) -> list[Task]:
        """Get all tasks with a specific priority."""
        query = (
            select(Task)
            .where(Task.priority == priority)
            .options(selectinload(Task.assigned_to_user))
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def mark_completed(
        self, db: AsyncSession, id: UUID
    ) -> Optional[Task]:
        """Mark task as completed."""
        task = await self.get(db, id)
        if task:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(datetime.now().astimezone().tzinfo)
            db.add(task)
            await db.commit()
            await db.refresh(task)
        return task

    async def filter_tasks(
        self,
        db: AsyncSession,
        project_id: Optional[UUID] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        assigned_to: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Task]:
        """Filter tasks by multiple criteria."""
        conditions = []

        if project_id:
            conditions.append(Task.project_id == project_id)
        if status:
            conditions.append(Task.status == status)
        if priority:
            conditions.append(Task.priority == priority)
        if assigned_to:
            conditions.append(Task.assigned_to == assigned_to)

        query = select(Task).offset(skip).limit(limit)

        if conditions:
            query = query.where(and_(*conditions))

        result = await db.execute(query)
        return result.scalars().all()


task_service = TaskService(Task)
