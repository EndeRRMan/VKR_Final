from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import SessionLocal
from fastapi import status

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    # Автоназначение, если assigned_to не указан
    assigned_to = task.assigned_to

    if assigned_to is None:
        employees = db.query(models.User).filter(models.User.role == models.RoleEnum.employee).all()
        if not employees:
            raise HTTPException(status_code=400, detail="Нет доступных сотрудников")

        def workload(user):
            active_tasks = db.query(models.Task).filter(
                models.Task.assigned_to == user.id,
                models.Task.status != models.StatusEnum.closed
            ).all()
            return sum(t.complexity for t in active_tasks) + len(active_tasks)

        assigned_to = min(employees, key=workload).id

    # Создаём ORM-модель задачи
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
def delete_task(task_id: int, db: Session = Depends(get_db)):
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
    task.assigned_to = task_update.assigned_to
    db.commit()
    db.refresh(task)
    return task