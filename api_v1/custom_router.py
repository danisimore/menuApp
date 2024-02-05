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
            # Пытаемся получить url с помощью имени и параметров запроса.
            url = self.url_path_for(router_name, **params)

            return url
        # Если получить url не удалось, то пробуем сгенерировать его на основе переданных параметров
        except NoMatchFound:
            # Получаем все пути роутера
            paths_list = self.get_paths_list()
            is_in_path = False
            # Итерируемся по списку всех путей
            for path in paths_list:
                # Итерируемся по именам переданных параметров
                for key in params.keys():
                    # Если хоть один параметр не содержится в пути, то is_in_path ставим в False и продолжаем итерации
                    # Если все параметры содержатся в запросе, то после итерации по параметрам is_in_path будет True
                    if key in path:
                        is_in_path = True
                    else:
                        is_in_path = False
                # Если is_in_path True
                if is_in_path:
                    url = path
                    # Форматируем url (в фигурные скобки проставляем значения параметров)
                    formatted_url = url.format(**params)

                    return formatted_url
            # Если в путях роутера не было пути с переданными параметрами, то выкидываем исключение
            raise NoMatchFound(name=router_name, path_params=params)
