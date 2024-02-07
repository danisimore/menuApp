"""
Модуль для расширения APIRouter..

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 06 февраля 2024
"""

from fastapi import APIRouter
from starlette.routing import NoMatchFound


class CustomAPIRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.routes_data = {}

    def get_paths_list(self) -> list:
        """
        Метод для получения списка всех путей роутера

        Returns:
            list - Список путей роутера
        """

        paths_list = []
        for route in self.routes:
            paths_list.append(route.path)

        return paths_list

    def reverse(self, router_name: str, **params) -> str:
        """
        Метод генерации пути на основе переданного имени пути и параметров.

        Если по указанному имени и параметрам путь не найден, то он будет генерироваться на основе параметров пути.
        Если у роутера нет пути с переданными параметрами, то будет возбуждено исключение.

        Args:
            router_name: название роутера
            **params: параметры пути

        Returns:
            URL, который был сгенерирован на основе переданного имени пути и параметров запроса.
        """
        try:
            url = self.url_path_for(router_name, **params)

            return url
        except NoMatchFound:
            paths_list = self.get_paths_list()
            is_in_path = False
            for path in paths_list:
                for key in params.keys():
                    if key in path:
                        is_in_path = True
                    else:
                        is_in_path = False

                if is_in_path:
                    url = path
                    formatted_url = url.format(**params)

                    return formatted_url

            raise NoMatchFound(name=router_name, path_params=params)
