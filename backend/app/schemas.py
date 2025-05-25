from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

# 🎭 Роли пользователей
class RoleEnum(str, Enum):
    employee = "employee"
    manager = "manager"
    admin = "admin"

# 📌 Статусы задач (должны совпадать с models.StatusEnum!)
class TaskStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"

# 🧩 Пользователи
class UserBase(BaseModel):
    username: str
    role: RoleEnum

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        from_attributes = True  # для Pydantic v2 (аналог orm_mode)

# 🧩 Задачи
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    complexity: int  # от 1 до 5

class TaskCreate(TaskBase):
    assigned_to: Optional[int] = None 

class Task(TaskBase):
    id: int
    status: TaskStatus
    assigned_to: Optional[int]

    class Config:
        from_attributes = True

# 📍 Смена статуса задачи
class TaskUpdateStatus(BaseModel):
    new_status: TaskStatus

# 📍 Переназначение задачи
class ReassignTask(BaseModel):
    new_user_id: int
