import pytest
import sys
import os
import time
import threading
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

# Добавляем путь к корневой папке проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Теперь импортируем с app.
from app.main import app, get_db
from app.database import Base
from app.config import settings

# Тестовая база данных
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


# Существующие тесты (оставляем как есть)
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
    # Создаем задачи
    client.post("/todos/", json={"title": "Задача 1"})
    client.post("/todos/", json={"title": "Задача 2"})

    response = client.get("/todos/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_filter_todos_by_completed():
    # Создаем завершенную и незавершенную задачи
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


# ИСПРАВЛЕННЫЕ ТЕСТЫ ДЛЯ HEALTH CHECK

def test_health_check():
    """Базовый тест health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()

    # Проверяем наличие всех полей
    assert "status" in data
    assert "database" in data
    assert "version" in data

    # Проверяем значения
    assert data["status"] == "healthy"
    assert data["version"] == settings.VERSION


def test_health_check_with_db_connection():
    """Тест health check с проверкой подключения к БД"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()

    # Проверяем структуру ответа
    assert data["status"] == "healthy"
    assert data["database"] == "connected"  # Должно быть connected
    assert data["version"] == settings.VERSION

    # Дополнительно проверяем, что БД действительно работает
    todo_response = client.post("/todos/", json={"title": "Проверка БД"})
    assert todo_response.status_code == 201


def test_health_check_db_disconnected(monkeypatch):
    """Тест health check когда БД недоступна"""

    # Создаем мок для сессии, которая выбрасывает исключение при execute
    class MockBrokenSession:
        def execute(self, *args, **kwargs):
            raise Exception("Database disconnected")

        def close(self):
            pass

    # Создаем функцию get_db, которая возвращает нашу сломанную сессию
    def broken_get_db():
        yield MockBrokenSession()

    # Подменяем зависимость get_db
    app.dependency_overrides[get_db] = broken_get_db

    try:
        # Делаем запрос
        response = client.get("/health")

        # Проверяем результаты
        assert response.status_code == 200
        data = response.json()

        # Проверяем что статус healthy, но БД отключена
        assert data["status"] == "healthy"
        assert "disconnected" in data["database"].lower() or "error" in data["database"].lower()
    finally:
        # ВАЖНО: всегда возвращаем обратно нормальную зависимость
        app.dependency_overrides[get_db] = override_get_db


def test_health_check_response_time():
    """Тест времени ответа health check (должен быть быстрым)"""
    start_time = time.time()
    response = client.get("/health")
    end_time = time.time()

    assert response.status_code == 200
    # Health check должен отвечать быстро (меньше 500ms для тестов)
    assert end_time - start_time < 0.5


def test_health_check_detailed_info():
    """Тест что health check возвращает достаточно информации"""
    response = client.get("/health")
    data = response.json()

    # Проверяем наличие важных полей
    expected_fields = ["status", "database", "version"]
    for field in expected_fields:
        assert field in data, f"Поле {field} отсутствует в ответе"

    # Проверяем типы данных
    assert isinstance(data["version"], str)
    assert isinstance(data["database"], str)


def test_concurrent_health_checks():
    """Тест что health check выдерживает параллельные запросы"""
    results = []
    exceptions = []

    def make_request():
        try:
            response = client.get("/health")
            results.append(response.status_code)
        except Exception as e:
            exceptions.append(str(e))

    # Создаем 10 потоков для параллельных запросов
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()

    # Ждем завершения всех потоков
    for thread in threads:
        thread.join()

    # Проверяем что не было исключений
    assert len(exceptions) == 0, f"Были исключения: {exceptions}"
    # Все запросы должны быть успешными
    assert all(status == 200 for status in results)
    assert len(results) == 10


def test_health_check_after_db_operation():
    """Тест health check после операций с БД"""

    # Сначала делаем несколько операций с БД
    for i in range(5):
        response = client.post("/todos/", json={"title": f"Задача {i}"})
        assert response.status_code == 201  # Проверяем что операции успешны

    # Проверяем что health check все еще работает
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["database"] == "connected"

    # Проверяем что данные сохранились
    todos_response = client.get("/todos/")
    todos_data = todos_response.json()
    assert len(todos_data) == 5
