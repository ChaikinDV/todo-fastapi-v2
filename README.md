# Todo API

**Todo API** — это современный REST API для управления задачами, построенный на FastAPI с использованием PostgreSQL, Docker и автоматическими миграциями.
Проект демонстрирует лучшие практики бэкенд-разработки.

## Особенности:

- ✅ Полный CRUD для задач
- ✅ Контейнеризация
- ✅ PostgreSQL по-умолчанию, SQLite для тестов
- ✅ Автоматические миграции
- ✅ Валидация данных
- ✅ Unit-тесты
- ✅ Качество кода: линтер + форматтер
- ✅ Pre-commit хуки для автоматической проверки
- ✅ Health check с проверкой базы данных

## Технический стек

- **Фреймворк** - FastAPI
- **База данных** - PostgreSQL / SQLite
- **ORM** - SQLAlchemy 2.0
- **Миграции** - Alembic
- **Контейнеризация** - Docker, Docker Compose
- **Линтер/Форматтер** - Ruff
- **Тестирование** - Pytest
- **Валидация** - Pydantic 2.0

## Быстрый старт

### Требования

- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)
- Git

### Установка и запуск

1. **Клонируй репозиторий:**
```bash

git clone https://github.com/ChaikinDV/todo-fastapi-v2.git
cd todo-fastapi-v2
```
2. **Создай файл с переменным окружением**
```bash

cp .env.example .env
```
3. **Запусти проект через Docker**
```bash

docker-compose up --build
```

4. **Проверь работу:**
- API доступен: http://localhost:8000
- Документация Swagger: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Локальный запуск без Docker
```bash

# Создай виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Установи зависимости
pip install -r requirements.txt

# Запусти тесты
pytest tests/ -v

# Запусти сервер
uvicorn app.main:app --reload
```


## Эндпоинты

| **Метод**  | **Эндпоинт** | **Описание**              | **Коды статуса** |
|--------|--------------|---------------------------|------------------|
| POST   | /todos/      | Создать новую задачу      | 201, 400         |
| GET    | /todos/      | Получить все задачи       | 200              |
| GET    | /todos/{id}  | Получить задачу по id     | 200, 404         |
| PUT    | /todos/{id}  | Обновить задачу           | 200, 404         |
| DELETE | /todos/{id}  | Удалить задачу            | 200, 404         |
| GET    | /health      | Проверка работоспособности | 200              |

## Тестирование

```bash

# Запуск тестов в контейнере
docker-compose exec app pytest tests/ -v

# Запуск тестов локально
pytest tests/ -v
```

## Структура проекта

### **todo-fastapi/**
**app/**
- ***__init__.py***
- ***main.py*** - FastAPI приложение
- ***database.py*** - Подключение к БД
- ***models.py*** - SQLAlchemy модели
- ***schemas.py*** - Pydantic схемы
- ***crud.py*** - CRUD операции
- ***config.py*** - Конфигурации приложения

**alembic/**
- ***versions/*** - Файлы миграций
- ***env.py***

**tests/**
- ***test_main.py***

**.env.example** - Пример переменных окружения

**.gitignore**

**.pre-commit-config.yaml**

**ruff.toml**

**requirements.txt**

**Dockerfile**

**docker-compose.yml**

**entrypoint.sh**

**README.md**
