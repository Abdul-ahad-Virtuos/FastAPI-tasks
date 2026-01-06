from enum import Enum
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, validator

class StatusEnum(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Title of the task (3-100 chars)")
    description: Optional[str] = Field(None, max_length=1000, description="Task description (max 1000 chars)")
    status: StatusEnum = Field(StatusEnum.todo, description="Task status")
    priority: PriorityEnum = Field(PriorityEnum.medium, description="Task priority")
    due_date: Optional[date] = Field(None, description="Due date (cannot be in the past)")

    @validator("due_date")
    def due_date_not_past(cls, v):
        if v and v < date.today():
            raise ValueError("due_date cannot be in the past")
        return v

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[StatusEnum] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[date] = None

    @validator("due_date")
    def due_date_not_past(cls, v):
        if v and v < date.today():
            raise ValueError("due_date cannot be in the past")
        return v

class TaskResponse(TaskBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
