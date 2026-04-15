from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Используем настройки из config.py
DATABASE_URL = settings.DATABASE_URL

# Создаём движок SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_size=5,  # Количество соединений в пуле
    max_overflow=10,  # Максимальное превышение пула
    pool_pre_ping=True,  # Проверка соединения перед использованием
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
