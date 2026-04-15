# Todo API

Готовый к использованию RESTful Todo API, созданный с использованием FastAPI и SQLAlchemy.
Прекрасный пример базовой backend разработки на Python.

## Особенности:

- **Полные CRUD операции** - Сreate, Read, Update, Delete
- **База данных SQL** - SQLite с SQLAlchemy ORM
- **Автоматическая документация API** - Интерактивный Swagger UI
- **Валидация данных** - валидация с помощью Pydantic
- **Unit-тесты** - все сценарии тестирования с использованием Pytest
- **Современный стек** - FastAPI, SQLAlchemy 2.0, Pydantic v2

## Технический стек

- **Backend**: FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Validation**: Pydantic
- **Testing**: Pytest
- **API Docs**: Swagger UI

## Установка и запуск

```bash
# Клонировать репозиторий
git clone https://github.com/ChaikinDV/todo-fastapi.git
cd todo-fastapi

# Установить зависимости
pip install -r requirements.txt

# Запуск сервера
uvicorn main:app --reload
```

## Эндпоинты

| **Метод**  | **Эндпоинт** | **Описание**               | **Коды статуса** |
|--------|--------------|----------------------------|------------------|
| POST   | /todos/      | Создать нровую задачу      | 201, 400         |
| GET    | /todos/      | Получить все задачи        | 200              |
| GET    | /todos/{id}  | Получить задачу по id      | 200, 404         |
| PUT    | /todos/{id}  | Обновить задачу            | 200, 404         |
| DELETE | /todos/{id}  | Удалить задачу             | 200, 404         |
| GET    | /health      | Проверка работоспособности | 200              |

## Тестирование

```bash
# Запуск тестов
pytest tests/ -v
```

## Документация API

После запуска сервера автоматическая документация доступна по адресу:

Swagger UI: http://localhost:8000/docs

## Структура проекта

### **todo-fastapi/**
- **main.py** - FastAPI приложение и маршруты
- **database.py** - Конфигурация базы данных
- **models.py** - SQLAlchemy модели
- **schemas.py** - Pydantic схемы
- **tests/test_main.py** - Unit-тесты
- **requirements.txt** - Зависимости
- **README.md** - Документация
