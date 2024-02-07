"""
Модуль для тестирования CRUD операций, связанных с меню.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 31 января 2024 | Добавлены тесты для сравнения ответа и данных из БД
"""
import pytest
from httpx import AsyncClient
from menu.router import router
from tests_services.menu_services_for_tests import (
    get_all_menus_data,
    get_menu_data_from_db_with_counters,
    get_menu_data_from_db_without_counters,
)
from tests_utils.fixtures import create_menu_using_post_method_fixture
from tests_utils.internal_tests import (
    assert_response,
    delete_object_internal_test,
    get_object_when_table_is_empty_internal_test,
    get_objects_when_table_is_not_empty_internal_test,
    get_specific_object_when_table_is_empty_internal_test,
)
from tests_utils.test_data import (
    MENU_DESCRIPTION_VALUE_TO_CREATE,
    MENU_DESCRIPTION_VALUE_TO_UPDATE,
    MENU_TITLE_VALUE_TO_CREATE,
    MENU_TITLE_VALUE_TO_UPDATE,
)
from tests_utils.utils import get_created_object_attribute


class TestGetMenusFromEmptyTable:
    @pytest.mark.asyncio
    async def test_get_menus_method_when_table_is_empty(self, ac: AsyncClient) -> None:
        """
        Тестирование события получения всех записей из таблицы menus, когда в таблице еще нет ни одной записи.

        Тест проходит успешно, если:
            1. Код ответа 200;
            2. В теле ответа - пустой список.

        Args:
            ac: клиент для асинхронных HTTP запросов.

        Returns:
            None
        """

        url = router.reverse(router_name='menu_base_url')

        response = await get_object_when_table_is_empty_internal_test(ac=ac, url=url)

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        menus = await get_all_menus_data()

        assert menus == response.json()


class TestCreateMenu:
    @pytest.mark.asyncio
    async def test_create_menu_using_post_method(
            self, ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
    ) -> None:
        """
        Тестирование создания меню, путем отправки POST запроса.

        Тест проходит успешно, если:
            1. Код ответа 201.
            2. title созданной записи, которую вернул сервер, совпадает с переданным title'ом в запросе.
            3. description созданной записи, которую вернул сервер, совпадает с переданным description'ом в запросе.

        Args:
            ac: клиент для асинхронных HTTP запросов.
            create_menu_using_post_method_fixture: фикстура, для отправки POST запроса и сохранения ответа сервера в кеше

        Returns:
            None
        """

        response = create_menu_using_post_method_fixture

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        menu_data = await get_menu_data_from_db_without_counters()
        assert menu_data == response.json()


class TestGetMenusFromTableWithData:
    @pytest.mark.asyncio
    async def test_get_menus_method_when_table_is_not_empty(self, ac: AsyncClient) -> None:
        """
        Тестирование события получения всех записей из таблицы menus, когда в таблице есть записи.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. Ответ содержит не пустой список.

        Args:
            ac: клиент для асинхронных HTTP запросов.

        Returns:
            None
        """

        url = router.reverse(router_name='menu_base_url')

        response = await get_objects_when_table_is_not_empty_internal_test(ac=ac, url=url)

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        menu_data = await get_all_menus_data()
        assert menu_data == response.json()


class TestGetSpecificMenu:
    @pytest.mark.asyncio
    async def test_get_specific_menu_method(
            self, ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
    ) -> None:
        """
        Тестирование получения определенной записи из таблицы menus по переданному параметру пути в запросе.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. title найденной записи, которую вернул сервер, совпадает title'ом созданной ранее записи.
            3. description найденной записи, которую вернул сервер, совпадает description'ом созданной ранее записи.
            4. В ответе были данные о подменю, количестве подменю, а также количестве блюд, связанных с меню через все
               подменю.

        Args:
            ac: клиент для асинхронных HTTP запросов.
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос
        Returns:
            None
        """

        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        url = router.reverse(router_name='menu_base_url', target_menu_id=target_menu_id)

        response = await ac.get(url=url)

        # Проверяем, что сервер вернул ожидаемые данные.
        assert_response(
            response=response,
            expected_status_code=200,
            expected_data={
                'id': target_menu_id,
                'title': MENU_TITLE_VALUE_TO_CREATE,
                'description': MENU_DESCRIPTION_VALUE_TO_CREATE,
                'submenus_count': 0,
                'dishes_count': 0,
            },
        )

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        menu = await get_menu_data_from_db_with_counters()
        assert menu == response.json()


class TestUpdateMenu:
    @pytest.mark.asyncio
    async def test_update_menu_using_patch_method(
            self, ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
    ) -> None:
        """
        Тестирование обновления записи с помощью отправки запроса с методом PATCH

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. id обновленной записи совпадает с id созданной ранее записи. Т.е. это должна быть одна и та же запись.
            3. title обновленной записи возвращаемой сервером, совпадает title'ом из константы, на которую старый title
               должен быть обновлен.
            4. description обновленной записи возвращаемой сервером, совпадает description'ом из константы, на которую
               старый description должен быть обновлен.

        Args:
            ac: клиент для асинхронных HTTP запросов.
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос
        Returns:
            None
        """

        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        url = router.reverse(router_name='menu_base_url', target_menu_id=target_menu_id)

        response = await ac.patch(
            url=url,
            json={
                'title': MENU_TITLE_VALUE_TO_UPDATE,
                'description': MENU_DESCRIPTION_VALUE_TO_UPDATE,
            },
        )

        assert_response(
            response=response,
            expected_status_code=200,
            expected_data={
                'id': target_menu_id,
                'title': MENU_TITLE_VALUE_TO_UPDATE,
                'description': MENU_DESCRIPTION_VALUE_TO_UPDATE,
            },
        )

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        menu_data = await get_menu_data_from_db_without_counters()
        assert menu_data == response.json()


class TestGetSpecificMenuAfterUpdate:
    @pytest.mark.asyncio
    async def test_get_specific_menu_method_after_update(
            self, ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
    ) -> None:
        """
        Тестирование получения определенной записи из таблицы menus по переданному параметру пути в запросе.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. title найденной записи, которую вернул сервер, совпадает title'ом обновленной ранее записи.
            3. description найденной записи, которую вернул сервер, совпадает description'ом обновленной ранее записи.
            4. В ответе были данные о подменю, количестве подменю, а также количестве блюд, связанных с меню через все
               подменю.

        Args:
            ac: клиент для асинхронных HTTP запросов,
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос
        Returns:
            None
        """

        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        url = router.reverse(router_name='menu_base_url', target_menu_id=target_menu_id)

        response = await ac.get(url=url)

        assert_response(
            response=response,
            expected_status_code=200,
            expected_data={
                'id': target_menu_id,
                'title': MENU_TITLE_VALUE_TO_UPDATE,
                'description': MENU_DESCRIPTION_VALUE_TO_UPDATE,
                'submenus_count': 0,
                'dishes_count': 0,
            },
        )

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        menu = await get_menu_data_from_db_with_counters()
        assert menu == response.json()


class TestDeleteMenu:
    @pytest.mark.asyncio
    async def test_delete_menu_method(
            self, ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
    ) -> None:
        """
        Тест удаления записи.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. Тело ответа от сервера == {"status": "success!"}

        Args:
            ac: клиент для асинхронных HTTP запросов.
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос.
        Returns:
            None
        """

        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        url = router.reverse(router_name='menu_base_url', target_menu_id=target_menu_id)

        await delete_object_internal_test(ac=ac, url=url)

        # Проверяем, чтобы данные были удалены
        menus_data = await get_all_menus_data()
        assert menus_data == []


class TestGetMenusAfterDelete:
    @pytest.mark.asyncio
    async def test_get_menus_method_after_delete(self, ac: AsyncClient) -> None:
        """
        Тестирование события получения всех записей из таблицы menus, когда запись была удалена из таблицы.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. Ответ содержит пустой список.

        Args:
            ac: клиент для асинхронных HTTP запросов.

        Returns:
            None
        """

        url = router.reverse(router_name='menu_base_url')

        response = await get_object_when_table_is_empty_internal_test(ac=ac, url=url)

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        menus_data = await get_all_menus_data()

        assert menus_data == response.json()


class TestGetSpecificMenuAfterDelete:
    @pytest.mark.asyncio
    async def test_get_specific_menu_method_after_delete(
            self, ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
    ) -> None:
        """
        Тестирование получения определенного меню по id, которого не существует в БД.

        Тест проходит успешно, если:
            1. Код ответа 404.
            2. Тело ответа от сервера == {"detail": "menu not found"}

        Args:
            ac: клиент для асинхронных HTTP запросов.
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос
        Returns:
            None
        """

        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        url = router.reverse(router_name='menu_base_url', target_menu_id=target_menu_id)

        # Используем тест, который получает не существующую запись.
        await get_specific_object_when_table_is_empty_internal_test(
            ac=ac, url=url, expected_data={'detail': 'menu not found'}
        )

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        menu_data = await get_all_menus_data()
        assert menu_data == []
