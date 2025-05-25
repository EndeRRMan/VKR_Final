from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class RoleEnum(str, enum.Enum):
    employee = "employee"
    manager = "manager"
    admin = "admin"

class StatusEnum(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"  # Правильное имя вместо "closed" / "created"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.employee)
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("Task", back_populates="assigned_user")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    complexity = Column(Integer, default=1)
    status = Column(Enum(StatusEnum), default=StatusEnum.open)
    created_at = Column(DateTime, default=datetime.utcnow)

    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_user = relationship("User", back_populates="tasks")

