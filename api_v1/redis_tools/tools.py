import json
import aioredis
from typing import Union


class RedisTools:

    def __init__(self):
        self.redis = None

    async def connect_redis(self) -> None:
        """
        Метод для создания подключения к Redis.

        Returns:
            None
        """

        if not self.redis:
            self.redis = await aioredis.from_url("redis://localhost:6379/0")
        return self.redis

    async def set_pair(self, key: str, value: Union[list, dict]) -> None:
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
            list_with_formatted_objects = await self.format_object_to_json(value)
            # И сериализуем в JSON
            json_value = json.dumps(list_with_formatted_objects)

        # Записываем в Redis по переданному ключу JSON объект с данными.
        await redis.set(key, json_value)

    async def get_pair(self, key) -> Union[list, None]:
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

    async def invalidate_cache(self, key) -> None:
        """
        Метод для инвалидации кэша в случае изменения/добавления/удаления записи.

        Args:
            key: ключ, по которому нужно инвалидировать кэш

        Returns:
            None
        """
        redis = await self.connect_redis()
        await redis.delete(key)

    @staticmethod
    async def format_object_to_json(objects_list) -> list:
        """
        Метод для приведение объектов в списке к типу dict.

        Args:
            objects_list: список с объектом

        Returns:
            Список объектов типа dict.
        """

        object_json = []
        for obj in objects_list:
            object_json.append(obj.json())

        return object_json
