#!/bin/bash

set -e

echo "Ждём готовности базы данных"
while ! nc -z db 5432; do
  echo "База данных ещё не готова, ждём 1 секунду..."
  sleep 1
done
echo "База данных готова!"

echo "Применяем миграции Alembic"
alembic upgrade head

echo "Запускаем приложение FastAPI"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
