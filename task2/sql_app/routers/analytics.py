"""
Comments and Analytics API routes.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from sql_app.db import get_session
from sql_app.schemas import (
    TaskCommentCreate,
    TaskCommentUpdate,
    TaskCommentResponse,
    TaskCommentDetailedResponse,
    ProjectAnalytics,
    UserWorkload,
    TaskDashboard,
)
from sql_app.services import task_comment_service, analytics_service

comment_router = APIRouter(prefix="/comments", tags=["comments"])
analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])


# ============================================================================
# COMMENT ROUTES
# ============================================================================


@comment_router.post("/", response_model=TaskCommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment: TaskCommentCreate,
    db: AsyncSession = Depends(get_session)
):
    """Create a new comment."""
    return await task_comment_service.create(db, comment)


@comment_router.get("/task/{task_id}", response_model=List[TaskCommentResponse])
async def get_task_comments(
    task_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """Get all comments for a task."""
    return await task_comment_service.get_task_comments(db, task_id)


@comment_router.get("/user/{user_id}", response_model=List[TaskCommentResponse])
async def get_user_comments(
    user_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """Get all comments by a user."""
    return await task_comment_service.get_user_comments(db, user_id)


@comment_router.get("/{comment_id}", response_model=TaskCommentDetailedResponse)
async def get_comment(comment_id: UUID, db: AsyncSession = Depends(get_session)):
    """Get comment with details."""
    comment = await task_comment_service.get_with_details(db, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return comment


@comment_router.put("/{comment_id}", response_model=TaskCommentResponse)
async def update_comment(
    comment_id: UUID,
    comment_update: TaskCommentUpdate,
    db: AsyncSession = Depends(get_session)
):
    """Update comment."""
    comment = await task_comment_service.update(db, comment_id, comment_update)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return comment


@comment_router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: UUID, db: AsyncSession = Depends(get_session)):
    """Delete comment."""
    comment = await task_comment_service.delete(db, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )


# ============================================================================
# ANALYTICS ROUTES
# ============================================================================


@analytics_router.get("/dashboard", response_model=TaskDashboard)
async def get_dashboard(db: AsyncSession = Depends(get_session)):
    """Get task dashboard with overview."""
    return await analytics_service.get_task_dashboard(db)


@analytics_router.get("/project/{project_id}", response_model=ProjectAnalytics)
async def get_project_analytics(
    project_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """Get analytics for a project."""
    analytics = await analytics_service.get_project_analytics(db, project_id)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return analytics


@analytics_router.get("/user/{user_id}", response_model=UserWorkload)
async def get_user_workload(
    user_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """Get workload analytics for a user."""
    workload = await analytics_service.get_user_workload(db, user_id)
    if not workload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return workload


@analytics_router.get("/overdue-tasks", response_model=List)
async def get_overdue_tasks(db: AsyncSession = Depends(get_session)):
    """Get all overdue tasks."""
    return await analytics_service.get_overdue_tasks(db)


@analytics_router.get("/completion-trend", response_model=dict)
async def get_completion_trend(
    days: int = 30,
    db: AsyncSession = Depends(get_session)
):
    """Get task completion trend for last N days."""
    return await analytics_service.get_completion_trend(db, days)
