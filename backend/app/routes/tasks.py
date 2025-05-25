from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import SessionLocal
from typing import Annotated
from app.dependencies import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.RoleEnum.manager:
        raise HTTPException(status_code=403, detail="Нет прав на создание задач")

    assigned_to = None
    employees = db.query(models.User).filter(models.User.role == models.RoleEnum.employee).all()
    if not employees:
        raise HTTPException(status_code=400, detail="Нет доступных сотрудников")

    def workload(user):
        active_tasks = db.query(models.Task).filter(
            models.Task.assigned_to == user.id,
            models.Task.status != models.StatusEnum.completed
        ).all()
        return sum(t.complexity for t in active_tasks) + len(active_tasks)

    assigned_to = min(employees, key=workload).id

    new_task = models.Task(
        title=task.title,
        description=task.description,
        complexity=task.complexity,
        assigned_to=assigned_to
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/", response_model=list[schemas.Task])
def read_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()
    return tasks

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.RoleEnum.manager:
        raise HTTPException(status_code=403, detail="Нет прав на удаление задач")

    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    db.delete(task)
    db.commit()
    return {"message": "Задача удалена"}

@router.put("/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task_update: schemas.TaskCreate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    task.title = task_update.title
    task.description = task_update.description
    task.complexity = task_update.complexity
    db.commit()
    db.refresh(task)
    return task

@router.patch("/{task_id}/status", response_model=schemas.Task)
def update_task_status(
    task_id: int,
    status_update: schemas.TaskUpdateStatus,
    db: Session = Depends(get_db),
    current_user = Annotated[models.User, Depends(get_current_user)]
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    if current_user.role != models.RoleEnum.employee or task.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав на изменение статуса")

    task.status = status_update.new_status
    db.commit()
    db.refresh(task)
    return task

@router.put("/{task_id}/reassign")
def reassign_task(
    task_id: int,
    new_user: schemas.ReassignTask,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.RoleEnum.manager:
        raise HTTPException(status_code=403, detail="Нет доступа")

    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    user = db.query(models.User).filter(models.User.id == new_user.new_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Новый пользователь не найден")

    task.assigned_to = new_user.new_user_id
    db.commit()
    db.refresh(task)
    return {"message": f"Задача переназначена на пользователя ID {user.id}"}

@router.patch("/{task_id}/status/by-manager", response_model=schemas.Task)
def update_status_by_manager(
    task_id: int,
    status_update: schemas.TaskUpdateStatus,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.RoleEnum.manager:
        raise HTTPException(status_code=403, detail="Нет доступа")

    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    task.status = status_update.new_status
    db.commit()
    db.refresh(task)
    return task
