"""
Модуль для тестирования CRUD операций, связанных с блюдами.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 31 января 2024 | Добавлены тесты для сравнения ответа и данных из БД
"""

import pytest
from dish.router import router as dish_router
from httpx import AsyncClient
from menu.router import router as menu_router
from submenu.router import router as submenu_router
from tests_services.dish_services_for_tests import (
    get_dish_by_index,
    get_specific_dish_data_from_db,
)
from tests_services.menu_services_for_tests import (
    get_all_menus_data,
    get_menu_data_from_db_without_counters,
)
from tests_services.submenu_services_for_tests import get_submenus_data_from_db
from tests_utils.fixtures import (
    create_dish_using_post_method_fixture,
    create_menu_using_post_method_fixture,
    create_submenu_using_post_method_fixture,
)
from tests_utils.internal_tests import (
    assert_response,
    delete_object_internal_test,
    get_object_when_table_is_empty_internal_test,
    get_objects_when_table_is_not_empty_internal_test,
    get_specific_object_when_table_is_empty_internal_test,
)
from tests_utils.test_data import (
    DISH_DESCRIPTION_VALUE_TO_CREATE,
    DISH_DESCRIPTION_VALUE_TO_UPDATE,
    DISH_PRICE_TO_CREATE,
    DISH_PRICE_TO_UPDATE,
    DISH_TITLE_VALUE_TO_CREATE,
    DISH_TITLE_VALUE_TO_UPDATE,
)
from tests_utils.utils import get_created_object_attribute


class TestCreateMenu:
    @pytest.mark.asyncio
    async def test_create_menu_from_dish_using_post_method(
            self, ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
    ) -> None:
        """
        Тестирование создания меню в рамках теста CRUD для блюд.

        Тест проходит успешно, если:
            1. Код ответа 201.
            2. title созданной записи, которую вернул сервер, совпадает с переданным title'ом в запросе.
            3. description созданной записи, которую вернул сервер, совпадает с переданным description'ом в запросе.

        Args:
            ac: клиент для асинхронных HTTP запросов.
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню

        Returns:
            None
        """

        response = create_menu_using_post_method_fixture

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        menu_data = await get_menu_data_from_db_without_counters()
        assert menu_data == response.json()


class TestCreateSubmenu:
    @pytest.mark.asyncio
    async def test_create_submenu_from_dish_using_post_method(
            self,
            ac: AsyncClient,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
    ) -> None:
        """
        Тестирование создания подменю в рамках теста CRUD для блюд.

        Тест проходит успешно, если:
            1. Код ответа 201.
            2. Данные из тела ответа соответствуют данным, переданным в запросе. Т.е. сервер вернул данные созданной записи
               и они соответствуют указанным.

        Args:
            ac: клиент для асинхронных HTTP запросов,

            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,

            create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,

        Returns:
            None
        """

        response = create_submenu_using_post_method_fixture

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        submenus_data = await get_submenus_data_from_db()
        assert submenus_data[0] == response.json()


class TestGetDishesFromEmptyTable:
    @pytest.mark.asyncio
    async def test_get_dishes_method_when_table_is_empty(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
    ) -> None:
        """
        Функция тестирует получение всех блюд для созданного подменю когда таблица dishes не содержит ни одной записи для
        этого подменю.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. Тело ответа от сервера - пустой список

        Args:
            ac: клиент для асинхронных HTTP запросов.
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
            create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,

        Returns:
            None
        """

        # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
        target_submenu_id = get_created_object_attribute(
            response=create_submenu_using_post_method_fixture, attribute='id'
        )

        url = dish_router.reverse(
            router_name='dish_get_method',
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id
        )

        response = await ac.get(
            url=url
        )

        assert_response(response=response, expected_status_code=200, expected_data=[])

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_dishes_from_db() -> None:
        """
        Метод проверяющий, что в БД нет записей в таблице dishes

        Returns:
            None
        """

        dishes_data = await get_dish_by_index(index=0)
        assert dishes_data == []


class TestCreateDish:
    @pytest.mark.asyncio
    async def test_create_dish_using_post_method(
            self,
            ac: AsyncClient,
            create_dish_using_post_method_fixture: create_dish_using_post_method_fixture,
    ) -> None:
        """
        Тестирование создания блюда, путем отправки POST запроса.

        Args:
            ac: клиент для асинхронных HTTP запросов.
            create_dish_using_post_method_fixture: фикстура, представляющая собой закешированый ответ сервера на POST
            запрос на создание блюда.

        Returns:
            None
        """

        response = create_dish_using_post_method_fixture

        dishes_data = await get_dish_by_index(index=0)
        assert dishes_data[0] == response.json()


class TestGetDishFromTableWithData:
    @pytest.mark.asyncio
    async def test_get_dishes_method_when_table_is_not_empty(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
    ) -> None:
        """
        Функция тестирует получение всех блюд для созданного подменю когда таблица dishes содержит записи для
        этого подменю.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. В теле ответа не пустой список.

        Args:
            ac: клиент для асинхронных HTTP запросов.
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
            create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,

        Returns:
            None
        """

        # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
        target_submenu_id = get_created_object_attribute(
            response=create_submenu_using_post_method_fixture, attribute='id'
        )

        url = dish_router.reverse(
            router_name='dish_base_url',
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id
        )

        response = await get_objects_when_table_is_not_empty_internal_test(
            ac=ac, url=url
        )

        response_json = response.json()

        dishes_data = await get_dish_by_index(index=0)
        assert dishes_data == response_json


class TestGetSpecificDish:
    @pytest.mark.asyncio
    async def test_get_specific_dish_method(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
            create_dish_using_post_method_fixture: create_dish_using_post_method_fixture,
    ) -> None:
        """
        Функция тестирует получение определенного блюда для созданного подменю.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. title найденной записи, которую вернул сервер, совпадает title'ом созданной ранее записи.
            3. description найденной записи, которую вернул сервер, совпадает description'ом созданной ранее записи.
            4. price найденной записи, которую вернул сервер, совпадает price'ом созданной ранее записи.
            5. submenu_id найденной записи, которую вернул сервер, совпадает menu_id созданной ранее записи.

        Args:
            ac: клиент для асинхронных HTTP запросов,
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
            create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,
            create_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание блюда,

        Returns:
            None
        """

        # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
        target_submenu_id = get_created_object_attribute(
            response=create_submenu_using_post_method_fixture, attribute='id'
        )

        # Получаем uuid, который вернул сервер после создания записи в таблице dishes с помощью фикстуры.
        target_dish_id = get_created_object_attribute(
            response=create_dish_using_post_method_fixture, attribute='id'
        )

        url = dish_router.reverse(
            router_name='dish_base_url',
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            target_dish_id=target_dish_id
        )

        response = await ac.get(
            url=url
        )

        assert_response(
            response=response,
            expected_status_code=200,
            expected_data={
                'id': target_dish_id,
                'title': DISH_TITLE_VALUE_TO_CREATE,
                'description': DISH_DESCRIPTION_VALUE_TO_CREATE,
                'price': str(DISH_PRICE_TO_CREATE),
                'submenu_id': target_submenu_id,
            },
        )

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        result = await get_specific_dish_data_from_db()
        dish_data = result.scalars().all()

        dish_data_json = await dish_data[0].json()

        assert dish_data_json == response.json()


class TestUpdateDish:
    @pytest.mark.asyncio
    async def test_update_dish_using_patch_method(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
            create_dish_using_post_method_fixture: create_dish_using_post_method_fixture,
    ) -> None:
        """
        Функция тестирует обновление определенного блюда с помощью отправки запроса с методом PATCH.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. id обновленной записи совпадает с id созданной ранее записи. Т.е. это должна быть одна и та же запись.
            3. title обновленной записи возвращаемой сервером, совпадает title'ом из константы, на которую старый title
               должен быть обновлен.
            4. description обновленной записи возвращаемой сервером, совпадает description'ом из константы, на которую
               старый description должен быть обновлен.
            5. price обновленной записи возвращаемой сервером, совпадает price'ом из константы, на которую
               старый price должен быть обновлен.
            6. submenu_id обновленной записи возвращаемой сервером, совпадает submenu_id из константы, на которую
               старый submenu_id должен быть обновлен.

        Args:
            ac: клиент для асинхронных HTTP запросов,
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
            create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,
            create_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание блюда,

        Returns:
            None
        """

        # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
        target_submenu_id = get_created_object_attribute(
            response=create_submenu_using_post_method_fixture, attribute='id'
        )

        # Получаем uuid, который вернул сервер после создания записи в таблице dishes с помощью фикстуры.
        target_dish_id = get_created_object_attribute(
            response=create_dish_using_post_method_fixture, attribute='id'
        )

        url = dish_router.reverse(
            router_name='dish_base_url',
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            target_dish_id=target_dish_id
        )

        response = await ac.patch(
            url=url,
            json={
                'title': DISH_TITLE_VALUE_TO_UPDATE,
                'description': DISH_DESCRIPTION_VALUE_TO_UPDATE,
                'price': str(DISH_PRICE_TO_UPDATE),
            },
        )

        assert_response(
            response=response,
            expected_status_code=200,
            expected_data={
                'id': target_dish_id,
                'title': DISH_TITLE_VALUE_TO_UPDATE,
                'description': DISH_DESCRIPTION_VALUE_TO_UPDATE,
                'price': str(DISH_PRICE_TO_UPDATE),
                'submenu_id': target_submenu_id,
            },
        )

        dishes_data = await get_dish_by_index(index=0)
        assert dishes_data[0] == response.json()


class TestGetSpecificDishAfterUpdate:
    @pytest.mark.asyncio
    async def test_get_specific_dish_method_after_update(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
            create_dish_using_post_method_fixture: create_dish_using_post_method_fixture,
    ) -> None:
        """
        Тестирование получения определенной записи из таблицы dishes по переданным параметрам пути запроса после обновления.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. title найденной записи, которую вернул сервер, совпадает title'ом обновленной ранее записи.
            3. description найденной записи, которую вернул сервер, совпадает description'ом обновленной ранее записи.
            4. price найденной записи, которую вернул сервер, совпадает price'ом обновленной ранее записи.
            5. submenu_id найденной записи, которую вернул сервер, совпадает submenu_id обновленной ранее записи.

        Args:
            ac: клиент для асинхронных HTTP запросов,
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
            create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,
            create_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание блюда,

        Returns:
            None
        """

        # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
        target_submenu_id = get_created_object_attribute(
            response=create_submenu_using_post_method_fixture, attribute='id'
        )

        # Получаем uuid, который вернул сервер после создания записи в таблице dishes с помощью фикстуры.
        target_dish_id = get_created_object_attribute(
            response=create_dish_using_post_method_fixture, attribute='id'
        )

        url = dish_router.reverse(
            router_name='dish_base_url',
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            target_dish_id=target_dish_id
        )

        response = await ac.get(
            url=url
        )

        assert_response(
            response=response,
            expected_status_code=200,
            expected_data={
                'id': target_dish_id,
                'title': DISH_TITLE_VALUE_TO_UPDATE,
                'description': DISH_DESCRIPTION_VALUE_TO_UPDATE,
                'price': str(DISH_PRICE_TO_UPDATE),
                'submenu_id': target_submenu_id,
            },
        )

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        result = await get_specific_dish_data_from_db()
        dish_data = result.scalars().all()

        dish_data_json = await dish_data[0].json()

        assert dish_data_json == response.json()


class TestDeleteDish:
    @pytest.mark.asyncio
    async def test_delete_dish_method(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
            create_dish_using_post_method_fixture: create_dish_using_post_method_fixture,
    ) -> None:
        """
        Тест удаления записи.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. Тело ответа от сервера == {"status": "success!"}

        Args:
            ac: клиент для асинхронных HTTP запросов,
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
            create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,
            create_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание блюда,

        Returns:
            None
        """

        # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
        target_submenu_id = get_created_object_attribute(
            response=create_submenu_using_post_method_fixture, attribute='id'
        )

        # Получаем uuid, который вернул сервер после создания записи в таблице dishes с помощью фикстуры.
        target_dish_id = get_created_object_attribute(
            response=create_dish_using_post_method_fixture, attribute='id'
        )

        url = dish_router.reverse(
            router_name='dish_base_url',
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            target_dish_id=target_dish_id
        )

        await delete_object_internal_test(
            ac=ac,
            url=url
        )

        dishes_data = await get_dish_by_index(index=0)
        assert dishes_data == []


class TestGetDishesAfterDelete:
    @pytest.mark.asyncio
    async def test_get_dishes_method_after_delete(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
    ) -> None:
        """
        Тестирование события получения всех записей из таблицы dishes, когда запись была удалена из таблицы.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. Ответ содержит пустой список

        Args:
            ac: клиент для асинхронных HTTP запросов,
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
            create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,

        Returns:
            None
        """

        # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
        target_submenu_id = get_created_object_attribute(
            response=create_submenu_using_post_method_fixture, attribute='id'
        )

        url = dish_router.reverse(
            router_name='dish_base_url',
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
        )

        response = await get_object_when_table_is_empty_internal_test(ac=ac, url=url)

        # Проверяем, что для созданного меню действительно не существует подменю
        dishes_data = await get_dish_by_index(index=0)
        assert dishes_data == response.json()


class GetSpecificDishAfterDelete:
    @pytest.mark.asyncio
    async def test_get_specific_dish_method_after_delete(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
            create_dish_using_post_method_fixture: create_dish_using_post_method_fixture,
    ) -> None:
        """
        Тестирование события получения определенной из таблицы dishes, когда запись была удалена из таблицы.

        Тест проходит успешно, если:
            1. Код ответа 404.
            2. Тело ответа от сервера == {"detail": "dish not found"}

        Args:
            ac: клиент для асинхронных HTTP запросов,
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
            create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,
            create_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание блюда,

        Returns:
            None
        """

        # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
        target_submenu_id = get_created_object_attribute(
            response=create_submenu_using_post_method_fixture, attribute='id'
        )

        # Получаем uuid, который вернул сервер после создания записи в таблице dishes с помощью фикстуры.
        target_dish_id = get_created_object_attribute(
            response=create_dish_using_post_method_fixture, attribute='id'
        )

        url = dish_router.reverse(
            router_name='dish_base_url',
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            target_dish_id=target_dish_id
        )

        response = await get_specific_object_when_table_is_empty_internal_test(
            ac=ac,
            url=url,
            expected_data={'detail': 'dish not found'},
        )

        # Проверяем, что для созданного меню действительно не существует подменю
        dishes_data = await get_specific_dish_data_from_db()
        assert dishes_data == response.json()


class TestDeleteSubmenu:
    @pytest.mark.asyncio
    async def test_delete_submenu_from_dish_method(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
    ) -> None:
        """
        Тестирование удаления подменю путем отправки запроса с методом DELETE.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. Тело ответа от сервера == {"status": "success!"}

        Args:
            ac: клиент для асинхронных HTTP запросов,
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
            create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,

        Returns:
            None
        """

        # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
        target_submenu_id = get_created_object_attribute(
            response=create_submenu_using_post_method_fixture, attribute='id'
        )

        url = submenu_router.reverse(
            router_name='dish_base_url',
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id
        )

        await delete_object_internal_test(
            ac=ac, url=url
        )

        # Проверяем, что для созданного меню действительно не существует подменю
        submenus_data = await get_submenus_data_from_db()
        assert submenus_data == []


class TestGetSubmenusAfterDelete:
    @pytest.mark.asyncio
    async def test_get_submenus_after_delete_from_dish_method(
            self, ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
    ) -> None:
        """
        Тестирование получения подменю после удаления.

        Тест проходит успешно, если:
            1. Код ответа 404.
            2. Тело ответа от сервера == {'detail': 'Not Found'}

        Args:
            ac: клиент для асинхронных HTTP запросов,
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,

        Returns:
            None
        """

        # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        url = submenu_router.reverse(
            router_name='dish_base_url',
            target_menu_id=target_menu_id,
        )

        response = await get_object_when_table_is_empty_internal_test(ac=ac, url=url)

        # Проверяем, что для созданного меню действительно не существует подменю
        submenus_data = await get_submenus_data_from_db()
        assert submenus_data == response.json()


class TestDeleteMenu:
    @pytest.mark.asyncio
    async def test_delete_menu_from_dish_method(
            self, ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
    ) -> None:
        """
        Тестирование удаления меню путем отправки запроса с методом DELETE.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. Тело ответа от сервера == {"status": "success!"}

        Args:
            ac: клиент для асинхронных HTTP запросов,
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,

        Returns:
            None
        """

        # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        url = menu_router.reverse(
            router_name='dish_base_url',
            target_menu_id=target_menu_id,
        )

        await delete_object_internal_test(ac=ac, url=url)

        # Проверяем, чтобы данные были удалены
        menus_data = await get_all_menus_data()
        assert menus_data == []


class TestGetMenusAfterDelete:
    @pytest.mark.asyncio
    async def test_get_menus_after_delete_from_dish_method(self, ac: AsyncClient) -> None:
        """
        Тестирование получения меню после удаления.

        Тест проходит успешно, если:
            1. Код ответа 200;
            2. В теле ответа - пустой список.

        Args:
            ac: клиент для асинхронных HTTP запросов,

        Returns:
            None
        """

        url = menu_router.reverse(
            router_name='menu_base_url',
        )

        response = await get_object_when_table_is_empty_internal_test(ac=ac, url=url)

        # Проверяем, чтобы данные были удалены
        menus_data = await get_all_menus_data()
        assert menus_data == response.json()
