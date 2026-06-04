from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import crud, schemas
from app.config import settings
from app.database import SessionLocal

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A professional Todo API built with FastAPI",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post(
    "/todos/",
    response_model=schemas.Todo,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую задачу",
)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    return crud.create_todo(db=db, todo=todo)


@app.get("/todos/", response_model=list[schemas.Todo], summary="Получить все задачи")
def read_todos(
    skip: int = 0, limit: int = 100, completed: bool | None = None, db: Session = Depends(get_db)
):
    todos = crud.get_todos(db, skip=skip, limit=limit, completed=completed)
    return todos


@app.get("/todos/{todo_id}", response_model=schemas.Todo, summary="Получить задачу по ID")
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = crud.get_todo(db, todo_id=todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail=f"Задача с ID {todo_id} не найдена")
    return db_todo


@app.put("/todos/{todo_id}", response_model=schemas.Todo, summary="Обновить задачу")
def update_todo(todo_id: int, todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    db_todo = crud.update_todo(db=db, todo_id=todo_id, todo=todo)
    if db_todo is None:
        raise HTTPException(status_code=404, detail=f"Задача с ID {todo_id} не найдена")
    return db_todo


@app.delete("/todos/{todo_id}", summary="Удалить задачу")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    success = crud.delete_todo(db=db, todo_id=todo_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Задача с ID {todo_id} не найдена")
    return {"message": "Задача успешно удалена"}


@app.get("/health", summary="Проверка работоспособности")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"

    return {"status": "healthy", "database": db_status, "version": settings.VERSION}
