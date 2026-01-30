"""
Project API routes.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from sql_app.db import get_session
from sql_app.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectDetailedResponse,
    ProjectAnalytics,
)
from sql_app.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate, db: AsyncSession = Depends(get_session)):
    """Create a new project."""
    return await project_service.create(db, project)


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
):
    """List all projects."""
    return await project_service.get_all(db, skip, limit)


@router.get("/list/active", response_model=List[ProjectResponse])
async def list_active_projects(db: AsyncSession = Depends(get_session)):
    """List active projects."""
    return await project_service.get_active_projects(db)


@router.get("/{project_id}", response_model=ProjectDetailedResponse)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_session)):
    """Get project with details."""
    project = await project_service.get_with_owner(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


@router.get("/owner/{owner_id}", response_model=List[ProjectResponse])
async def get_projects_by_owner(
    owner_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """Get all projects owned by a user."""
    return await project_service.get_by_owner(db, owner_id)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_session)
):
    """Update project."""
    project = await project_service.update(db, project_id, project_update)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: UUID, db: AsyncSession = Depends(get_session)):
    """Delete project (hard delete)."""
    project = await project_service.delete(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )


@router.patch("/{project_id}/deactivate", response_model=ProjectResponse)
async def deactivate_project(project_id: UUID, db: AsyncSession = Depends(get_session)):
    """Soft delete project (mark inactive)."""
    project = await project_service.soft_delete(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


@router.get("/{project_id}/stats", response_model=ProjectAnalytics)
async def get_project_stats(project_id: UUID, db: AsyncSession = Depends(get_session)):
    """Get project statistics."""
    stats = await project_service.get_project_stats(db, project_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return stats
