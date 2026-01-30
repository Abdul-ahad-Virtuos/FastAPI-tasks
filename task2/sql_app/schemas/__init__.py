"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, field_validator

from sql_app.models import TaskStatus, TaskPriority


# ============================================================================
# PAGINATION
# ============================================================================


class PaginationParams(BaseModel):
    """Pagination parameters."""
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    total: int
    skip: int
    limit: int
    items: List


# ============================================================================
# USER SCHEMAS
# ============================================================================


class UserCreate(BaseModel):
    """User creation schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v):
        assert v.isalnum() or "_" in v, "Username must be alphanumeric"
        return v


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User response schema."""
    id: UUID
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# TAG SCHEMAS
# ============================================================================


class TagCreate(BaseModel):
    """Tag creation schema."""
    name: str = Field(..., min_length=1, max_length=100)
    color: Optional[str] = "#808080"

    @field_validator("color")
    @classmethod
    def validate_color(cls, v):
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("Color must be hex format (e.g., #808080)")
        return v


class TagUpdate(BaseModel):
    """Tag update schema."""
    name: Optional[str] = None
    color: Optional[str] = None


class TagResponse(BaseModel):
    """Tag response schema."""
    id: UUID
    name: str
    color: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# PROJECT SCHEMAS
# ============================================================================


class ProjectCreate(BaseModel):
    """Project creation schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    owner_id: UUID


class ProjectUpdate(BaseModel):
    """Project update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProjectResponse(BaseModel):
    """Project response schema."""
    id: UUID
    name: str
    description: Optional[str]
    owner_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectDetailedResponse(ProjectResponse):
    """Detailed project response with nested relations."""
    owner: UserResponse
    task_count: Optional[int] = 0
    completed_tasks: Optional[int] = 0


# ============================================================================
# TASK SCHEMAS
# ============================================================================


class TaskCreate(BaseModel):
    """Task creation schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    project_id: UUID
    assigned_to: Optional[UUID] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None

    @field_validator("due_date", mode="before")
    @classmethod
    def validate_due_date(cls, v):
        if v and v <= datetime.now():
            raise ValueError("Due date must be in the future")
        return v


class TaskUpdate(BaseModel):
    """Task update schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[UUID] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    """Task response schema."""
    id: UUID
    title: str
    description: Optional[str]
    project_id: UUID
    assigned_to: Optional[UUID]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskDetailedResponse(TaskResponse):
    """Detailed task response with nested relations."""
    project: ProjectResponse
    assigned_to_user: Optional[UserResponse]
    tags: List[TagResponse] = []
    assignments: List["TaskAssignmentResponse"] = []
    comments: List["TaskCommentResponse"] = []


# ============================================================================
# TASK ASSIGNMENT SCHEMAS
# ============================================================================


class TaskAssignmentCreate(BaseModel):
    """Task assignment creation schema."""
    task_id: UUID
    user_id: UUID
    hours_allocated: Optional[int] = None


class TaskAssignmentResponse(BaseModel):
    """Task assignment response schema."""
    id: UUID
    task_id: UUID
    user_id: UUID
    assigned_by: Optional[UUID]
    assigned_at: datetime
    hours_allocated: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# TASK COMMENT SCHEMAS
# ============================================================================


class TaskCommentCreate(BaseModel):
    """Task comment creation schema."""
    task_id: UUID
    content: str = Field(..., min_length=1, max_length=5000)


class TaskCommentUpdate(BaseModel):
    """Task comment update schema."""
    content: Optional[str] = Field(None, min_length=1, max_length=5000)


class TaskCommentResponse(BaseModel):
    """Task comment response schema."""
    id: UUID
    task_id: UUID
    created_by: UUID
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskCommentDetailedResponse(TaskCommentResponse):
    """Detailed task comment response."""
    created_by_user: UserResponse


# ============================================================================
# ANALYTICS SCHEMAS
# ============================================================================


class ProjectAnalytics(BaseModel):
    """Project analytics schema."""
    project_id: UUID
    project_name: str
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    overdue_tasks: int
    completion_percentage: float


class UserWorkload(BaseModel):
    """User workload schema."""
    user_id: UUID
    username: str
    assigned_tasks: int
    completed_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    total_hours_allocated: int


class TaskDashboard(BaseModel):
    """Task dashboard schema."""
    pending_count: int
    in_progress_count: int
    completed_count: int
    overdue_count: int
    total_by_priority: dict
    total_by_project: dict
    upcoming_tasks: List[TaskResponse]


# Update forward refs
TaskDetailedResponse.model_rebuild()
