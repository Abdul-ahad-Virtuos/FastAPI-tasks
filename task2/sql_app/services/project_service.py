"""
Project CRUD service.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sql_app.models import Project, Task, TaskStatus
from sql_app.schemas import ProjectCreate, ProjectUpdate
from sql_app.services.base import BaseCRUDService


class ProjectService(BaseCRUDService[Project, ProjectCreate, ProjectUpdate]):
    """Project CRUD service."""

    async def get_with_owner(self, db: AsyncSession, id: UUID) -> Optional[Project]:
        """Get project with owner details."""
        query = select(Project).where(Project.id == id).options(selectinload(Project.owner))
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by_owner(self, db: AsyncSession, owner_id: UUID) -> list[Project]:
        """Get all projects for an owner."""
        query = (
            select(Project)
            .where(Project.owner_id == owner_id)
            .options(selectinload(Project.owner))
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_active_projects(self, db: AsyncSession) -> list[Project]:
        """Get all active projects."""
        query = select(Project).where(Project.is_active == True)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_project_stats(self, db: AsyncSession, project_id: UUID) -> dict:
        """Get project statistics."""
        project = await self.get(db, project_id)
        if not project:
            return {}

        # Count tasks by status
        query = select(
            Task.status,
            func.count(Task.id).label("count")
        ).where(Task.project_id == project_id).group_by(Task.status)

        result = await db.execute(query)
        stats = {row[0]: row[1] for row in result.all()}

        total_tasks = sum(stats.values())
        completed = stats.get(TaskStatus.COMPLETED, 0)

        return {
            "project_id": project_id,
            "project_name": project.name,
            "total_tasks": total_tasks,
            "completed_tasks": completed,
            "pending_tasks": stats.get(TaskStatus.PENDING, 0),
            "in_progress_tasks": stats.get(TaskStatus.IN_PROGRESS, 0),
            "cancelled_tasks": stats.get(TaskStatus.CANCELLED, 0),
            "completion_percentage": (completed / total_tasks * 100) if total_tasks > 0 else 0,
        }

    async def soft_delete(self, db: AsyncSession, id: UUID) -> Optional[Project]:
        """Soft delete project (mark inactive)."""
        project = await self.get(db, id)
        if project:
            project.is_active = False
            db.add(project)
            await db.commit()
            await db.refresh(project)
        return project


project_service = ProjectService(Project)
