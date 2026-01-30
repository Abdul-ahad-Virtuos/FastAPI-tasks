"""
Analytics service for advanced queries.
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sql_app.models import Task, TaskStatus, TaskPriority, Project, User, TaskAssignment
from sql_app.schemas import ProjectAnalytics, UserWorkload, TaskDashboard


class AnalyticsService:
    """Analytics and reporting service."""

    @staticmethod
    async def get_project_analytics(
        db: AsyncSession, project_id: UUID
    ) -> Optional[ProjectAnalytics]:
        """Get comprehensive project analytics."""
        project = await db.get(Project, project_id)
        if not project:
            return None

        # Count tasks by status
        query = select(
            Task.status,
            func.count(Task.id).label("count")
        ).where(Task.project_id == project_id).group_by(Task.status)

        result = await db.execute(query)
        stats = {row[0]: row[1] for row in result.all()}

        total_tasks = sum(stats.values())
        completed = stats.get(TaskStatus.COMPLETED, 0)
        pending = stats.get(TaskStatus.PENDING, 0)
        in_progress = stats.get(TaskStatus.IN_PROGRESS, 0)

        # Count overdue tasks
        now = datetime.now(datetime.now().astimezone().tzinfo)
        overdue_query = select(func.count(Task.id)).where(
            and_(
                Task.project_id == project_id,
                Task.due_date < now,
                Task.status != TaskStatus.COMPLETED,
                Task.status != TaskStatus.CANCELLED,
            )
        )
        overdue_result = await db.execute(overdue_query)
        overdue_count = overdue_result.scalar()

        return ProjectAnalytics(
            project_id=project_id,
            project_name=project.name,
            total_tasks=total_tasks,
            completed_tasks=completed,
            pending_tasks=pending,
            in_progress_tasks=in_progress,
            overdue_tasks=overdue_count,
            completion_percentage=(completed / total_tasks * 100) if total_tasks > 0 else 0.0,
        )

    @staticmethod
    async def get_user_workload(
        db: AsyncSession, user_id: UUID
    ) -> Optional[UserWorkload]:
        """Get user workload analytics."""
        user = await db.get(User, user_id)
        if not user:
            return None

        # Count tasks by status
        query = select(
            Task.status,
            func.count(Task.id).label("count")
        ).where(Task.assigned_to == user_id).group_by(Task.status)

        result = await db.execute(query)
        stats = {row[0]: row[1] for row in result.all()}

        # Get total hours allocated
        hours_query = select(func.sum(TaskAssignment.hours_allocated)).where(
            TaskAssignment.user_id == user_id
        )
        hours_result = await db.execute(hours_query)
        total_hours = hours_result.scalar() or 0

        return UserWorkload(
            user_id=user_id,
            username=user.username,
            assigned_tasks=sum(stats.values()),
            completed_tasks=stats.get(TaskStatus.COMPLETED, 0),
            pending_tasks=stats.get(TaskStatus.PENDING, 0),
            in_progress_tasks=stats.get(TaskStatus.IN_PROGRESS, 0),
            total_hours_allocated=total_hours,
        )

    @staticmethod
    async def get_task_dashboard(db: AsyncSession) -> TaskDashboard:
        """Get overall task dashboard."""
        # Count by status
        status_query = select(
            Task.status,
            func.count(Task.id).label("count")
        ).group_by(Task.status)

        status_result = await db.execute(status_query)
        status_stats = {row[0]: row[1] for row in status_result.all()}

        # Count by priority
        priority_query = select(
            Task.priority,
            func.count(Task.id).label("count")
        ).group_by(Task.priority)

        priority_result = await db.execute(priority_query)
        priority_stats = {str(row[0]): row[1] for row in priority_result.all()}

        # Count by project
        project_query = select(
            Project.name,
            func.count(Task.id).label("count")
        ).select_from(Task).join(Project).group_by(Project.name)

        project_result = await db.execute(project_query)
        project_stats = {row[0]: row[1] for row in project_result.all()}

        # Get upcoming tasks (next 7 days)
        now = datetime.now(datetime.now().astimezone().tzinfo)
        future = now + timedelta(days=7)

        upcoming_query = (
            select(Task)
            .where(
                and_(
                    Task.due_date.between(now, future),
                    Task.status != TaskStatus.COMPLETED,
                )
            )
            .options(selectinload(Task.assigned_to_user), selectinload(Task.project))
            .order_by(Task.due_date)
            .limit(10)
        )
        upcoming_result = await db.execute(upcoming_query)
        upcoming_tasks = upcoming_result.scalars().all()

        # Count overdue
        now = datetime.now(datetime.now().astimezone().tzinfo)
        overdue_query = select(func.count(Task.id)).where(
            and_(
                Task.due_date < now,
                Task.status != TaskStatus.COMPLETED,
                Task.status != TaskStatus.CANCELLED,
            )
        )
        overdue_result = await db.execute(overdue_query)
        overdue_count = overdue_result.scalar()

        return TaskDashboard(
            pending_count=status_stats.get(TaskStatus.PENDING, 0),
            in_progress_count=status_stats.get(TaskStatus.IN_PROGRESS, 0),
            completed_count=status_stats.get(TaskStatus.COMPLETED, 0),
            overdue_count=overdue_count,
            total_by_priority=priority_stats,
            total_by_project=project_stats,
            upcoming_tasks=upcoming_tasks,
        )

    @staticmethod
    async def get_overdue_tasks(db: AsyncSession) -> list[Task]:
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
            .options(
                selectinload(Task.assigned_to_user),
                selectinload(Task.project),
            )
            .order_by(Task.due_date)
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_tasks_by_date_range(
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime,
    ) -> list[Task]:
        """Get tasks created within a date range."""
        query = (
            select(Task)
            .where(Task.created_at.between(start_date, end_date))
            .options(selectinload(Task.assigned_to_user), selectinload(Task.project))
            .order_by(Task.created_at.desc())
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_completion_trend(
        db: AsyncSession,
        days: int = 30,
    ) -> dict:
        """Get task completion trend for last N days."""
        now = datetime.now(datetime.now().astimezone().tzinfo)
        start_date = now - timedelta(days=days)

        query = select(
            func.date(Task.completed_at).label("date"),
            func.count(Task.id).label("count")
        ).where(
            and_(
                Task.completed_at.isnot(None),
                Task.completed_at >= start_date,
            )
        ).group_by(func.date(Task.completed_at)).order_by("date")

        result = await db.execute(query)
        return {str(row[0]): row[1] for row in result.all()}


analytics_service = AnalyticsService()
