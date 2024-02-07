"""
Модуль для реализации подключения к Redis и выполнения операций в БД.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 06 февраля 2024
"""

import json
from typing import Any

import aioredis
from config import IS_TEST, REDIS_HOST, TEST_REDIS_HOST
from utils import format_object_to_json


class RedisTools:
    def __init__(self):
        self.redis = None

    async def connect_redis(self) -> aioredis.Redis:
        """
        Метод для создания подключения к Redis.

        Returns:
            Объект клиента Redis.
        """

        host = TEST_REDIS_HOST if IS_TEST else REDIS_HOST

        if not self.redis:
            self.redis = await aioredis.from_url(f'redis://localhost:6379/0')
        return self.redis

    async def set_pair(self, key: str, value: list[Any] | dict[Any, Any]) -> None:
        """
        Метод для сохранения объекта/объектов в кэше.

        Args:
            key: ключ, по которому можно получить доступ к значению объекта/объектов
            value: значение объекта/объектов

        Returns:
            None
        """

        redis = await self.connect_redis()

        if not len(value) or type(value) is dict:
            json_value = json.dumps(value)
        else:
            list_with_formatted_objects = await format_object_to_json(value)
            json_value = json.dumps(list_with_formatted_objects)

        await redis.set(key, json_value)

    async def get_pair(self, key: str) -> list[dict[Any, Any]] | dict[Any, Any] | None:
        """
        Метод для получения значения по переданному ключу.

        Args:
            key: ключ, по которому должно хранится значение

        Returns:
            Если по указанному ключу найдено значение, то list, иначе None
        """

        redis = await self.connect_redis()

        cache = await redis.get(key)

        if cache:
            cache_list = json.loads(cache)

            return cache_list

        return None

    async def invalidate_cache(self, key: str) -> None:
        """
        Метод для инвалидации кэша в случае изменения/добавления/удаления записи.

        Args:
            key: ключ, по которому нужно инвалидировать кэш

        Returns:
            None
        """
        redis = await self.connect_redis()
        await redis.delete(key)

    async def invalidate_all_cache(self) -> None:
        """
        Удаляет все данные

        :return: None
        """
        redis = await self.connect_redis()
        await redis.flushall()
