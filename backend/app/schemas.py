from pydantic import BaseModel
from typing import Optional
from enum import Enum
from pydantic import Field

class RoleEnum(str, Enum):
    employee = "employee"
    manager = "manager"
    admin = "admin"

class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    complexity: int = Field(default=1, ge=1, le=5)


class TaskCreate(TaskBase):
    assigned_to: Optional[int] = None  # None → автоназначение
    title: str
    description: Optional[str] = None
    complexity: int = Field(default=1, ge=1, le=5)

class Task(TaskBase):
    id: int
    status: str
    assigned_to: Optional[int]
    class Config:
        orm_mode = True
