import pytest
import sys
import os
import time
import threading
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app, get_db
from app.database import Base
from app.config import settings

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
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
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_todo():
    response = client.post("/todos/", json={
        "title": "Тестовая задача",
        "description": "Описание задачи",
        "completed": False
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Тестовая задача"
    assert "id" in data


def test_read_todos():
    client.post("/todos/", json={"title": "Задача 1"})
    client.post("/todos/", json={"title": "Задача 2"})

    response = client.get("/todos/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_filter_todos_by_completed():
    client.post("/todos/", json={"title": "Задача 1", "completed": False})
    client.post("/todos/", json={"title": "Задача 2", "completed": True})

    response = client.get("/todos/?completed=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["completed"] == True


def test_read_todo_not_found():
    response = client.get("/todos/999")
    assert response.status_code == 404
    assert "не найдена" in response.json()["detail"]



def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert "database" in data
    assert "version" in data

    assert data["status"] == "healthy"
    assert data["version"] == settings.VERSION


def test_health_check_with_db_connection():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["version"] == settings.VERSION

    todo_response = client.post("/todos/", json={"title": "Проверка БД"})
    assert todo_response.status_code == 201


def test_health_check_db_disconnected(monkeypatch):

    class MockBrokenSession:
        def execute(self, *args, **kwargs):
            raise Exception("Database disconnected")

        def close(self):
            pass

    def broken_get_db():
        yield MockBrokenSession()

    app.dependency_overrides[get_db] = broken_get_db

    try:
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "disconnected" in data["database"].lower() or "error" in data["database"].lower()
    finally:
        app.dependency_overrides[get_db] = override_get_db


def test_health_check_response_time():
    start_time = time.time()
    response = client.get("/health")
    end_time = time.time()

    assert response.status_code == 200
    assert end_time - start_time < 0.5


def test_health_check_detailed_info():
    response = client.get("/health")
    data = response.json()

    expected_fields = ["status", "database", "version"]
    for field in expected_fields:
        assert field in data, f"Поле {field} отсутствует в ответе"

    assert isinstance(data["version"], str)
    assert isinstance(data["database"], str)


def test_concurrent_health_checks():
    results = []
    exceptions = []

    def make_request():
        try:
            response = client.get("/health")
            results.append(response.status_code)
        except Exception as e:
            exceptions.append(str(e))

    threads = []
    for _ in range(10):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    assert len(exceptions) == 0, f"Были исключения: {exceptions}"
    assert all(status == 200 for status in results)
    assert len(results) == 10


def test_health_check_after_db_operation():

    for i in range(5):
        response = client.post("/todos/", json={"title": f"Задача {i}"})
        assert response.status_code == 201

    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["database"] == "connected"

    todos_response = client.get("/todos/")
    todos_data = todos_response.json()
    assert len(todos_data) == 5
