"""
SQLAlchemy ORM models for task management system.
"""
from datetime import datetime
from enum import Enum
from typing import List

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Table,
    Index,
    Enum as SQLEnum,
    CheckConstraint,
    UniqueConstraint,
    Integer,
    Boolean,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref

from sql_app.models.base import BaseModel


# ============================================================================
# ENUMS
# ============================================================================


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================================
# JUNCTION TABLES
# ============================================================================


task_tags = Table(
    "task_tags",
    BaseModel.metadata,
    Column("task_id", UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

Index("idx_task_tags_task_id", task_tags.c.task_id)
Index("idx_task_tags_tag_id", task_tags.c.tag_id)


# ============================================================================
# USER MODEL
# ============================================================================


class User(BaseModel):
    """User model."""
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True, index=True)

    # Relationships
    tasks = relationship(
        "Task",
        back_populates="assigned_to_user",
        foreign_keys="Task.assigned_to",
    )
    assignments = relationship("TaskAssignment", back_populates="user")
    comments = relationship("TaskComment", back_populates="created_by_user")

    __table_args__ = (
        UniqueConstraint("email", name="uq_user_email"),
        UniqueConstraint("username", name="uq_user_username"),
    )


# ============================================================================
# PROJECT MODEL
# ============================================================================


class Project(BaseModel):
    """Project model."""
    __tablename__ = "projects"

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)

    # Relationships
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    owner = relationship("User")

    __table_args__ = (
        Index("idx_project_owner_id", "owner_id"),
        Index("idx_project_is_active", "is_active"),
    )


# ============================================================================
# TASK MODEL
# ============================================================================


class Task(BaseModel):
    """Task model."""
    __tablename__ = "tasks"

    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False, index=True)
    due_date = Column(DateTime(timezone=True), nullable=True, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    assigned_to_user = relationship(
        "User",
        back_populates="tasks",
        foreign_keys=[assigned_to],
    )
    assignments = relationship("TaskAssignment", back_populates="task", cascade="all, delete-orphan")
    tags = relationship(
        "Tag",
        secondary=task_tags,
        back_populates="tasks",
    )
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_task_project_id", "project_id"),
        Index("idx_task_assigned_to", "assigned_to"),
        Index("idx_task_status", "status"),
        Index("idx_task_priority", "priority"),
        Index("idx_task_due_date", "due_date"),
        Index("idx_task_project_status", "project_id", "status"),
        CheckConstraint("due_date IS NULL OR completed_at IS NULL OR completed_at <= due_date"),
    )


# ============================================================================
# TAG MODEL
# ============================================================================


class Tag(BaseModel):
    """Tag model."""
    __tablename__ = "tags"

    name = Column(String(100), unique=True, nullable=False, index=True)
    color = Column(String(7), default="#808080")  # Hex color code

    # Relationships
    tasks = relationship(
        "Task",
        secondary=task_tags,
        back_populates="tags",
    )

    __table_args__ = (
        UniqueConstraint("name", name="uq_tag_name"),
    )


# ============================================================================
# TASK ASSIGNMENT MODEL
# ============================================================================


class TaskAssignment(BaseModel):
    """Task assignment model (for multi-user assignment)."""
    __tablename__ = "task_assignments"

    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    hours_allocated = Column(Integer, nullable=True)

    # Relationships
    task = relationship("Task", back_populates="assignments")
    user = relationship(
        "User",
        back_populates="assignments",
        foreign_keys=[user_id],
    )

    __table_args__ = (
        UniqueConstraint("task_id", "user_id", name="uq_task_user_assignment"),
        Index("idx_assignment_task_id", "task_id"),
        Index("idx_assignment_user_id", "user_id"),
    )


# ============================================================================
# TASK COMMENT MODEL
# ============================================================================


class TaskComment(BaseModel):
    """Task comment model."""
    __tablename__ = "task_comments"

    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)

    # Relationships
    task = relationship("Task", back_populates="comments")
    created_by_user = relationship("User", back_populates="comments")

    __table_args__ = (
        Index("idx_comment_task_id", "task_id"),
        Index("idx_comment_created_by", "created_by"),
        Index("idx_comment_created_at", "created_at"),
    )
