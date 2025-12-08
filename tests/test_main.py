import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, get_db
from database import Base

# Тестовая база данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    # Создаем таблицы перед каждым тестом
    Base.metadata.create_all(bind=engine)
    yield
    # Удаляем таблицы после каждого теста
    Base.metadata.drop_all(bind=engine)


# Тест создания задачи
def test_create_todo():
    response = client.post("/todos/", json={
        "title": "Test Todo",
        "description": "Test Description",
        "completed": False
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "Test Description"
    assert data["completed"] == False
    assert "id" in data


# Тест получения списка всех задач
def test_get_todos():
    client.post("/todos/", json={
        "title": "Test Todo 1",
        "description": "Test Description 1"
    })
    client.post("/todos/", json={
        "title": "Test Todo 2",
        "description": "Test Description 2"
    })

    response = client.get("/todos/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["title"] == "Test Todo 1"
    assert data[1]["title"] == "Test Todo 2"


# Тест получения задачи по id
def test_get_todo_by_id():
    client.post("/todos/", json={
        "title": "Test Todo",
        "description": "Test Description"
    })

    response = client.get("/todos/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Test Todo"


# Тест получения несуществующей задачи
def test_get_todo_not_found():
    response = client.get("/todos/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


# Тест обновления задачи
def test_update_todo():
    client.post("/todos/", json={
        "title": "Old Title",
        "description": "Old Description",
        "completed": False
    })

    response = client.put("/todos/1", json={
        "title": "Updated Title",
        "description": "Updated Description",
        "completed": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"
    assert data["completed"] == True
    assert data["id"] == 1


# Тест обновления несуществующей задачи
def test_update_todo_not_found():
    response = client.put("/todos/999", json={
        "title": "Updated Title",
        "description": "Updated Description"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


# Тест удаления задачи
def test_delete_todo():
    client.post("/todos/", json={
        "title": "Test Todo",
        "description": "Test Description"
    })

    response = client.get("/todos/1")
    assert response.status_code == 200

    response = client.delete("/todos/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Todo deleted successfully"

    response = client.get("/todos/1")
    assert response.status_code == 404


# Тест удаления несуществующей задачи
def test_delete_todo_not_found():
    response = client.delete("/todos/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


# Тест основного эндпоинта
def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Todo API is running"


# Тест health check эндпоинта
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"