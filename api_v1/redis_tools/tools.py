"""
Модуль для реализации подключения к Redis и выполнения операций в БД.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 06 февраля 2024
"""

import json
from typing import Any

import aioredis
from config import REDIS_PORT, TEST_REDIS_PORT
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

        port = REDIS_PORT if REDIS_PORT else TEST_REDIS_PORT

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

        # Если прилетает пустой список или словарь (определенный объект)
        if not len(value) or type(value) is dict:
            # То сериализуем этот объект в JSON
            json_value = json.dumps(value)
        # Иначе прилетает список с объектами.
        else:
            # Приводим их к типу словаря, пользуясь объявленным в модели методом json.
            list_with_formatted_objects = await format_object_to_json(value)
            # И сериализуем в JSON
            json_value = json.dumps(list_with_formatted_objects)

        # Записываем в Redis по переданному ключу JSON объект с данными.
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

        # Получаем из Redis JSON объект по указанному ключу.
        cache = await redis.get(key)

        # Если по указанному ключу есть сохраненный объект, то десериализуем его в объект Python и возвращаем
        if cache:
            cache_list = json.loads(cache)

            return cache_list
        # Если ничего не нашлось, то возвращаем None
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
