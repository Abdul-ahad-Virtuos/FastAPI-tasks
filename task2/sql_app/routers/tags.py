"""
Tag and Assignment API routes.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from sql_app.db import get_session
from sql_app.schemas import (
    TagCreate,
    TagUpdate,
    TagResponse,
    TaskAssignmentCreate,
    TaskAssignmentResponse,
)
from sql_app.services import tag_service, task_assignment_service

tag_router = APIRouter(prefix="/tags", tags=["tags"])
assignment_router = APIRouter(prefix="/assignments", tags=["assignments"])


# ============================================================================
# TAG ROUTES
# ============================================================================


@tag_router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(tag: TagCreate, db: AsyncSession = Depends(get_session)):
    """Create a new tag."""
    existing = await tag_service.get_by_name(db, tag.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag name already exists"
        )
    return await tag_service.create(db, tag)


@tag_router.get("/", response_model=List[TagResponse])
async def list_tags(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
):
    """List all tags."""
    return await tag_service.get_all(db, skip, limit)


@tag_router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: UUID, db: AsyncSession = Depends(get_session)):
    """Get tag by ID."""
    tag = await tag_service.get(db, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return tag


@tag_router.get("/name/{name}", response_model=TagResponse)
async def get_tag_by_name(name: str, db: AsyncSession = Depends(get_session)):
    """Get tag by name."""
    tag = await tag_service.get_by_name(db, name)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return tag


@tag_router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: UUID,
    tag_update: TagUpdate,
    db: AsyncSession = Depends(get_session)
):
    """Update tag."""
    tag = await tag_service.update(db, tag_id, tag_update)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return tag


@tag_router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: UUID, db: AsyncSession = Depends(get_session)):
    """Delete tag."""
    tag = await tag_service.delete(db, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )


@tag_router.post("/{tag_id}/attach/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def attach_tag_to_task(
    tag_id: UUID,
    task_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """Attach tag to task."""
    success = await tag_service.attach_to_task(db, tag_id, task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag or task not found"
        )


@tag_router.delete("/{tag_id}/detach/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def detach_tag_from_task(
    tag_id: UUID,
    task_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """Detach tag from task."""
    success = await tag_service.detach_from_task(db, tag_id, task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )


# ============================================================================
# ASSIGNMENT ROUTES
# ============================================================================


@assignment_router.post("/", response_model=TaskAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment: TaskAssignmentCreate,
    db: AsyncSession = Depends(get_session)
):
    """Assign user to task."""
    return await task_assignment_service.create(db, assignment)


@assignment_router.get("/task/{task_id}", response_model=List[TaskAssignmentResponse])
async def get_task_assignments(
    task_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """Get all assignments for a task."""
    return await task_assignment_service.get_task_assignments(db, task_id)


@assignment_router.get("/user/{user_id}", response_model=List[TaskAssignmentResponse])
async def get_user_assignments(
    user_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """Get all assignments for a user."""
    return await task_assignment_service.get_user_assignments(db, user_id)


@assignment_router.delete("/task/{task_id}/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_assignment(
    task_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """Remove assignment."""
    success = await task_assignment_service.remove_assignment(db, task_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
