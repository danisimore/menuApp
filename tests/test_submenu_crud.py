"""
Модуль для тестирования CRUD операций, связанных с подменю.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 31 января 2024 | Добавлены тесты для сравнения ответа и данных из БД
"""

import pytest
from httpx import AsyncClient
from menu.router import router as menu_router
from submenu.router import router as submenu_router
from tests_services.menu_services_for_tests import (
    get_all_menus_data,
    get_menu_data_from_db_without_counters,
)
from tests_services.submenu_services_for_tests import (
    get_specific_submenu_data_from_db,
    get_submenus_data_from_db,
)
from tests_utils.fixtures import (
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
    SUBMENU_DESCRIPTION_VALUE_TO_CREATE,
    SUBMENU_DESCRIPTION_VALUE_TO_UPDATE,
    SUBMENU_TITLE_VALUE_TO_CREATE,
    SUBMENU_TITLE_VALUE_TO_UPDATE,
)
from tests_utils.utils import get_created_object_attribute


class TestCreateMenu:
    @pytest.mark.asyncio
    async def test_create_menu_from_submenu_using_post_method(
            self, ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
    ) -> None:
        """
        Тестирование создания меню в рамках теста CRUD для подменю.

        Тест проходит успешно, если:
            1. Код ответа 201.
            2. title созданной записи, которую вернул сервер, совпадает с переданным title'ом в запросе.
            3. description созданной записи, которую вернул сервер, совпадает с переданным description'ом в запросе.

        Args:
            ac: клиент для асинхронных HTTP запросов.
            create_menu_using_post_method_fixture: фикстура, представляющая собой закешированый ответ сервера на POST
            запрос на создание меню.

        Returns:
            None
        """

        response = create_menu_using_post_method_fixture

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        menu_data = await get_menu_data_from_db_without_counters()
        assert menu_data == response.json()


class TestGetSubmenusFromEmptyTable:
    @pytest.mark.asyncio
    async def test_get_submenus_for_created_menu_method_when_table_is_empty(
            self, ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
    ) -> None:
        """
        Функция тестирует получение всех подменю для созданного меню когда таблица submenus не содержит ни одной записи для
        этого меню.

        Тест проходит успешно, если:
            1. Код ответа 404.
            2. Тело ответа от сервера == {'detail': 'Not Found'}

        Args:
            ac: клиент для асинхронных HTTP запросов.
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню
        Returns:
            None
        """

        # Получаем uuid, который вернул сервер после создания записи в таблице menus с помощью фикстуры.
        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        url = submenu_router.reverse(
            router_name='submenu_base_url',
            target_menu_id=target_menu_id
        )

        response = await ac.get(url=url)

        assert_response(
            response=response,
            expected_status_code=200,
            expected_data=[],
        )

        # Проверяем, что для созданного меню действительно не существует подменю
        submenus_data = await get_submenus_data_from_db()
        assert submenus_data == []


class TestCreateSubmenu:
    @pytest.mark.asyncio
    async def test_create_submenu_using_post_method(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
    ) -> None:
        """
        Тестирование создания подменю, путем отправки POST запроса.

        Тест проходит успешно, если:
            1. Код ответа 201.
            2. Данные из тела ответа соответствуют данным, переданным в запросе. Т.е. сервер вернул данные созданной записи
               и они соответствуют указанным.

        Args:
            ac: клиент для асинхронных HTTP запросов,

            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,

            create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю

        Returns:
            None
        """

        response = create_submenu_using_post_method_fixture

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        submenus_data = await get_submenus_data_from_db()
        assert submenus_data[0] == response.json()


class GetSubmenusFromTableWithData:
    @pytest.mark.asyncio
    async def test_get_submenus_method_when_table_is_not_empty(
            self, ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
    ) -> None:
        """
        Функция тестирует получение всех подменю для созданного меню когда таблица submenus содержит записи для
        этого меню.

            Тест проходит успешно, если:
            1. Код ответа 200.
            2. В теле ответа не пустой список.

        Args:
            ac: клиент для асинхронных HTTP запросов.

            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,

        Returns:
            None
        """

        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        url = submenu_router.reverse(
            router_name='submenu_base_url',
            target_menu_id=target_menu_id
        )

        response = await get_objects_when_table_is_not_empty_internal_test(
            ac=ac, url=url
        )

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        submenus_data = await get_submenus_data_from_db()
        assert submenus_data == response.json()


class TestGetSpecificSubmenu:
    @pytest.mark.asyncio
    async def test_get_specific_submenu_method(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
    ) -> None:
        """
        Функция тестирует получение определенного подменю для созданного меню.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. title найденной записи, которую вернул сервер, совпадает title'ом созданной ранее записи.
            3. description найденной записи, которую вернул сервер, совпадает description'ом созданной ранее записи.
            4. menu_id найденной записи, которую вернул сервер, совпадает menu_id созданной ранее записи.
            5. В ответе были данные о блюдах и их количестве

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
            router_name='submenu_base_url',
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id
        )

        response = await ac.get(url=url)

        assert_response(
            response=response,
            expected_status_code=200,
            expected_data={
                'id': target_submenu_id,
                'title': SUBMENU_TITLE_VALUE_TO_CREATE,
                'description': SUBMENU_DESCRIPTION_VALUE_TO_CREATE,
                'menu_id': target_menu_id,
                'dishes': [],
                'dishes_count': 0,
            },
        )

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        submenus_data = await get_specific_submenu_data_from_db()
        submenus_data_json = await submenus_data.json()
        assert submenus_data_json == response.json()


class TestUpdateSubmenu:
    @pytest.mark.asyncio
    async def test_update_submenu_using_patch_method(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
    ) -> None:
        """
        Функция тестирует обновление определенного подменю с помощью отправки запроса с методом PATCH.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. id обновленной записи совпадает с id созданной ранее записи. Т.е. это должна быть одна и та же запись.
            3. title обновленной записи возвращаемой сервером, совпадает title'ом из константы, на которую старый title
               должен быть обновлен.
            4. description обновленной записи возвращаемой сервером, совпадает description'ом из константы, на которую
               старый description должен быть обновлен.

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
            router_name='submenu_base_url',
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id
        )

        response = await ac.patch(
            url=url,
            json={
                'title': SUBMENU_TITLE_VALUE_TO_UPDATE,
                'description': SUBMENU_DESCRIPTION_VALUE_TO_UPDATE,
            },
        )

        assert_response(
            response=response,
            expected_status_code=200,
            expected_data={
                'id': target_submenu_id,
                'title': SUBMENU_TITLE_VALUE_TO_UPDATE,
                'description': SUBMENU_DESCRIPTION_VALUE_TO_UPDATE,
                'menu_id': target_menu_id,
                'dishes': [],
            },
        )

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        submenus_data = await get_submenus_data_from_db()
        assert submenus_data[0] == response.json()


class TestGetSpecificSubmenuAfterUpdate:
    @pytest.mark.asyncio
    async def test_get_specific_submenu_method_after_update(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
    ) -> None:
        """
        Тестирование получения определенной записи из таблицы submenus по переданным параметрам пути в запросе.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. title найденной записи, которую вернул сервер, совпадает title'ом обновленной ранее записи.
            3. description найденной записи, которую вернул сервер, совпадает description'ом обновленной ранее записи.
            4. В ответе были данные о блюдах и их количестве

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
            router_name='submenu_base_url',
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id
        )

        response = await ac.get(url=url)

        assert_response(
            response=response,
            expected_status_code=200,
            expected_data={
                'id': target_submenu_id,
                'title': SUBMENU_TITLE_VALUE_TO_UPDATE,
                'description': SUBMENU_DESCRIPTION_VALUE_TO_UPDATE,
                'menu_id': target_menu_id,
                'dishes': [],
                'dishes_count': 0,
            },
        )

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        submenus_data = await get_specific_submenu_data_from_db()
        submenus_json_data = await submenus_data.json()
        assert submenus_json_data == response.json()


class TestDeleteSubmenu:
    @pytest.mark.asyncio
    async def test_delete_submenu_method(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
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
            router_name='submenu_base_url',
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
    async def test_get_submenus_method_after_delete(
            self, ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
    ) -> None:
        """
        Тестирование события получения всех записей из таблицы submenus, когда запись была удалена из таблицы.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. Ответ содержит пустой список

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
            router_name='submenu_base_url',
            target_menu_id=target_menu_id,
        )
        response = await get_object_when_table_is_empty_internal_test(ac=ac, url=url)

        # Проверяем, что для созданного меню действительно не существует подменю
        submenus_data = await get_submenus_data_from_db()
        assert submenus_data == response.json()


class TestGetSpecificSubmenuAfterDelete:
    @pytest.mark.asyncio
    async def test_get_specific_submenu_method_after_delete(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
    ) -> None:
        """
        Тестирование события получения определенной из таблицы submenus, когда запись была удалена из таблицы.

        Тест проходит успешно, если:
            1. Код ответа 404.
            2. Тело ответа от сервера == {"detail": "submenu not found"}

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
            router_name='submenu_base_url',
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id
        )

        response = await get_specific_object_when_table_is_empty_internal_test(
            ac=ac,
            url=url,
            expected_data={'detail': 'submenu not found'},
        )

        # Проверяем, что для созданного меню действительно не существует подменю
        submenus_data = await get_specific_submenu_data_from_db()
        assert submenus_data == response.json()


class TestDeleteMenu:
    @pytest.mark.asyncio
    async def test_delete_menu_from_submenu_method(
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
            router_name='menu_base_url',
            target_menu_id=target_menu_id,
        )

        await delete_object_internal_test(ac=ac, url=url)

        # Проверяем, чтобы данные были удалены
        menus_data = await get_all_menus_data()
        assert menus_data == []


class TestGetMenusAfterDelete:
    @pytest.mark.asyncio
    async def test_get_menus_after_delete_from_submenu_method(self, ac: AsyncClient) -> None:
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
