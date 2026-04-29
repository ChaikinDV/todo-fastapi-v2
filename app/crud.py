from sqlalchemy.orm import Session

import app.schemas as schemas
from app import models


def get_todo(db: Session, todo_id: int):
    return db.query(models.Todo).filter(models.Todo.id == todo_id).first()


def get_todos(
    db: Session, skip: int = 0, limit: int = 100, completed: bool | None = None
) -> list[models.Todo]:
    query = db.query(models.Todo)

    if completed is not None:
        query = query.filter(models.Todo.completed == completed)

    return query.offset(skip).limit(limit).all()


def create_todo(db: Session, todo: schemas.TodoCreate):
    db_todo = models.Todo(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def update_todo(db: Session, todo_id: int, todo: schemas.TodoCreate):
    db_todo = get_todo(db, todo_id)
    if db_todo:
        for field, value in todo.model_dump().items():
            setattr(db_todo, field, value)
        db.commit()
        db.refresh(db_todo)
    return db_todo


def delete_todo(db: Session, todo_id: int):
    db_todo = get_todo(db, todo_id)
    if db_todo:
        db.delete(db_todo)
        db.commit()
        return True
    return False
