"""
Модуль для создания подключения к базе данных.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 22 января 2024
"""

from typing import AsyncGenerator

from sqlalchemy import MetaData

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DB_HOST, DB_USER, DB_NAME, DB_PORT, DB_PASSWORD


DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

Base = declarative_base()
metadata = MetaData()

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Функция для получения асинхронной сессии подключения к БД."""
    async with async_session_maker() as session:
        yield session
