"""
Конфигурация фабричной функции для подключения к тестовой базе данных, а также асинхронного клиента для отправки
тестовых HTTP запросов

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 27 января 2024
"""

from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import TEST_DB_USER, TEST_DB_NAME, TEST_DB_HOST, TEST_DB_PORT, TEST_DB_PASSWORD
from database.database import get_async_session
from dish.models import Dish
from main import app

DATABASE_URL = (
    f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
)

test_engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session_maker = sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)
Dish.metadata.bind = test_engine


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Dish.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Dish.metadata.drop_all)


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
