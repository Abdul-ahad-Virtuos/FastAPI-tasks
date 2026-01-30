"""
Task API routes.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from sql_app.db import get_session
from sql_app.models import TaskStatus, TaskPriority
from sql_app.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskDetailedResponse,
)
from sql_app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_session)):
    """Create a new task."""
    return await task_service.create(db, task)


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
):
    """List all tasks."""
    return await task_service.get_all(db, skip, limit)


@router.get("/{task_id}", response_model=TaskDetailedResponse)
async def get_task(task_id: UUID, db: AsyncSession = Depends(get_session)):
    """Get task with all details."""
    task = await task_service.get_with_relations(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.get("/project/{project_id}", response_model=List[TaskResponse])
async def get_project_tasks(
    project_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """Get all tasks in a project."""
    return await task_service.get_by_project(db, project_id)


@router.get("/assignee/{user_id}", response_model=List[TaskResponse])
async def get_user_tasks(
    user_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """Get all tasks assigned to a user."""
    return await task_service.get_by_assignee(db, user_id)


@router.get("/status/{status}", response_model=List[TaskResponse])
async def get_tasks_by_status(
    status: TaskStatus,
    db: AsyncSession = Depends(get_session)
):
    """Get all tasks with a specific status."""
    return await task_service.get_by_status(db, status)


@router.get("/priority/{priority}", response_model=List[TaskResponse])
async def get_tasks_by_priority(
    priority: TaskPriority,
    db: AsyncSession = Depends(get_session)
):
    """Get all tasks with a specific priority."""
    return await task_service.get_by_priority(db, priority)


@router.get("/list/overdue", response_model=List[TaskResponse])
async def get_overdue_tasks(db: AsyncSession = Depends(get_session)):
    """Get all overdue tasks."""
    return await task_service.get_overdue_tasks(db)


@router.get("/list/upcoming", response_model=List[TaskResponse])
async def get_upcoming_tasks(
    days: int = 7,
    db: AsyncSession = Depends(get_session)
):
    """Get upcoming tasks due within specified days."""
    return await task_service.get_upcoming_tasks(db, days)


@router.post("/filter", response_model=List[TaskResponse])
async def filter_tasks(
    project_id: Optional[UUID] = None,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assigned_to: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
):
    """Filter tasks by multiple criteria."""
    return await task_service.filter_tasks(
        db,
        project_id=project_id,
        status=status,
        priority=priority,
        assigned_to=assigned_to,
        skip=skip,
        limit=limit,
    )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_session)
):
    """Update task."""
    task = await task_service.update(db, task_id, task_update)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(task_id: UUID, db: AsyncSession = Depends(get_session)):
    """Mark task as completed."""
    task = await task_service.mark_completed(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID, db: AsyncSession = Depends(get_session)):
    """Delete task."""
    task = await task_service.delete(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
