# Базовый образ с Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
# netcat-openbsd - утилита nc для проверки портов
# libpq-dev - нужна для psycopg2 (PostgreSQL)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем скрипт запуска и делаем его исполняемым
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Копируем весь код приложения
COPY . .

# Указываем порт
EXPOSE 8000

# Точка входа: запускаем entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

# Копируем файлы с зависимостями
COPY requirements.txt requirements-dev.txt ./

# Устанавливаем зависимости (и продакшен, и dev)
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt
