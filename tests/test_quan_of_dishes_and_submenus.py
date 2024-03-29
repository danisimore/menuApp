"""
Модуль для тестирования сценария проверки кол-ва блюд и подменю в меню.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 08 февраля 2024 | Добавлено тестирование всех меню со всеми связанными подменю и со всеми связанными блюдами
"""

import pytest
from dish.router import router as dish_router
from httpx import AsyncClient
from menu.router import router as menu_router
from submenu.router import router as submenu_router
from submenu.submenu_utils import format_dishes
from tests_services.dish_services_for_tests import get_dish_by_index
from tests_services.menu_services_for_tests import (
    get_all_menus_data,
    get_all_menus_detail_data,
    get_menu_data_from_db_with_counters,
    get_menu_data_from_db_without_counters,
)
from tests_services.submenu_services_for_tests import (
    get_specific_submenu_data_from_db,
    get_submenus_data_from_db,
)
from tests_utils.fixtures import (
    create_dish_using_post_method_fixture,
    create_menu_using_post_method_fixture,
    create_second_dish_using_post_method_fixture,
    create_submenu_using_post_method_fixture,
)
from tests_utils.internal_tests import (
    assert_response,
    delete_object_internal_test,
    get_object_when_table_is_empty_internal_test,
)
from tests_utils.test_data import (
    DISH_DESCRIPTION_VALUE_TO_CREATE,
    DISH_PRICE_TO_CREATE,
    DISH_TITLE_VALUE_TO_CREATE,
    MENU_DESCRIPTION_VALUE_TO_CREATE,
    MENU_TITLE_VALUE_TO_CREATE,
    SECOND_DISH_DESCRIPTION_VALUE_TO_CREATE,
    SECOND_DISH_PRICE_TO_CREATE,
    SECOND_DISH_TITLE_VALUE_TO_CREATE,
    SUBMENU_DESCRIPTION_VALUE_TO_CREATE,
    SUBMENU_TITLE_VALUE_TO_CREATE,
)
from tests_utils.utils import get_created_object_attribute


class TestCreateMenu:
    @pytest.mark.asyncio
    async def test_create_menu_from_check_quan_of_dishes_and_submenus_using_post_method(
            self, ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
    ) -> None:
        """
        Тестирование создания меню в рамках теста проверки количества блюд и подменю в меню.

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


class TestCreateSubmenu:
    @pytest.mark.asyncio
    async def test_create_submenu_from_check_quan_of_dishes_and_submenus_using_post_method(
            self,
            ac: AsyncClient,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
    ) -> None:
        """
        Тестирование создания подменю в рамках теста проверки количества блюд и подменю в меню.

        Тест проходит успешно, если:
            1. Код ответа 201.
            2. Данные из тела ответа соответствуют данным, переданным в запросе. Т.е. сервер вернул данные созданной
               записи и они соответствуют указанным.

        Args:
            ac: клиент для асинхронных HTTP запросов,
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,

        Returns:
            None
        """

        response = create_submenu_using_post_method_fixture

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        submenus_data = await get_submenus_data_from_db()
        assert submenus_data[0] == response.json()


class TestCreateFirstDish:
    @pytest.mark.asyncio
    async def test_create_first_dish_from_check_quan_of_dishes_and_submenus_using_post_method(
            self,
            ac: AsyncClient,
            create_dish_using_post_method_fixture: create_dish_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
    ) -> None:
        """
        Тестирование создания первого блюда в рамках теста проверки количества блюд и подменю в меню.

        Args:
            ac: клиент для асинхронных HTTP запросов,
            create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,
            create_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание блюда,

        Returns:
            None
        """

        response = create_dish_using_post_method_fixture

        # Проверяем, что ответ на POST запрос совпадает с сохраненными в БД данными
        dishes_data = await get_dish_by_index(index=0)

        assert dishes_data[0] == response.json()


class TestCreateSecondDish:
    @pytest.mark.asyncio
    async def test_create_second_dish_from_check_quan_of_dishes_and_submenus_using_post_method(
            self,
            ac: AsyncClient,
            create_second_dish_using_post_method_fixture: create_second_dish_using_post_method_fixture,
    ) -> None:
        """
        Тестирование создания второго блюда в рамках теста проверки количества блюд и подменю в меню.

        Args:
            ac: клиент для асинхронных HTTP запросов,
            create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,
            create_second_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание блюда,

        Returns:
            None
        """

        response = create_second_dish_using_post_method_fixture

        # Проверяем, что ответ на POST запрос совпадает с сохраненными в БД данными
        dishes_data = await get_dish_by_index(index=1)
        assert dishes_data[0] == response.json()


class TestGetMenusDetail:
    @pytest.mark.asyncio
    async def test_get_menus_detail(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
            create_dish_using_post_method_fixture: create_dish_using_post_method_fixture,
            create_second_dish_using_post_method_fixture: create_second_dish_using_post_method_fixture,
    ) -> None:
        """
        Тестирование эндпоинта для вывода всех меню со всеми связанными подменю и со всеми связанными блюдами

        :param ac: клиент для асинхронных HTTP запросов,
        :param create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню
        :param create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю
        :param create_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание 1-го блюда
        :param create_second_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание
                                                             2-го блюда
        :return: None
        """

        url = '/api/v1/menus/detail'
        response = await ac.get(url=url)

        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )
        target_submenu_id = get_created_object_attribute(
            response=create_submenu_using_post_method_fixture, attribute='id'
        )
        first_dish_id = get_created_object_attribute(
            response=create_dish_using_post_method_fixture, attribute='id'
        )
        second_dish_id = get_created_object_attribute(
            response=create_second_dish_using_post_method_fixture, attribute='id'
        )

        assert_response(
            response=response,
            expected_status_code=200,
            expected_data=[{
                'id': target_menu_id,
                'title': MENU_TITLE_VALUE_TO_CREATE,
                'description': MENU_DESCRIPTION_VALUE_TO_CREATE,
                'submenus': [
                    {
                        'id': target_submenu_id,
                        'title': SUBMENU_TITLE_VALUE_TO_CREATE,
                        'description': SUBMENU_DESCRIPTION_VALUE_TO_CREATE,
                        'menu_id': target_menu_id,
                        'dishes_count': 2,
                        'dishes': [
                            {
                                'id': first_dish_id,
                                'title': DISH_TITLE_VALUE_TO_CREATE,
                                'description': DISH_DESCRIPTION_VALUE_TO_CREATE,
                                'price': str(DISH_PRICE_TO_CREATE),
                                'submenu_id': target_submenu_id
                            },
                            {
                                'id': second_dish_id,
                                'title': SECOND_DISH_TITLE_VALUE_TO_CREATE,
                                'description': SECOND_DISH_DESCRIPTION_VALUE_TO_CREATE,
                                'price': str(SECOND_DISH_PRICE_TO_CREATE),
                                'submenu_id': target_submenu_id
                            }
                        ]
                    }
                ]
            }],
        )

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        menus_detail_json_data = await get_all_menus_detail_data()
        assert response.json() == menus_detail_json_data


class TestGetSpecificMenu:
    @pytest.mark.asyncio
    async def test_get_specific_menu_from_check_quan_of_dishes_and_submenus_method(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
            create_dish_using_post_method_fixture: create_dish_using_post_method_fixture,
            create_second_dish_using_post_method_fixture: create_second_dish_using_post_method_fixture,
    ) -> None:
        """
        Функция тестирует получение определенного меню в рамках теста проверки количества блюд и подменю в меню.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. title найденной записи, которую вернул сервер, совпадает title'ом созданной ранее записи.
            3. description найденной записи, которую вернул сервер, совпадает description'ом созданной ранее записи.
            4. В ответе были данные о подменю, количестве подменю, а также количестве блюд, связанных с меню через все
               подменю.

        Args:
            ac: клиент для асинхронных HTTP запросов,
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
            create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,
            create_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание блюда,
            create_second_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание 2-ого
                                                          блюда,

        Returns:
            None
        """

        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        url = menu_router.reverse(router_name='menu_base_url', target_menu_id=target_menu_id)

        response = await ac.get(url=url)

        assert_response(
            response=response,
            expected_status_code=200,
            expected_data={
                'id': target_menu_id,
                'title': MENU_TITLE_VALUE_TO_CREATE,
                'description': MENU_DESCRIPTION_VALUE_TO_CREATE,
                'submenus_count': 1,
                'dishes_count': 2,
            },
        )

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        menu = await get_menu_data_from_db_with_counters()
        assert menu == response.json()


class TestGetSpecificSubmenu:
    @pytest.mark.asyncio
    async def test_get_specific_submenu_from_check_quan_of_dishes_and_submenus_method(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
            create_dish_using_post_method_fixture: create_dish_using_post_method_fixture,
            create_second_dish_using_post_method_fixture: create_second_dish_using_post_method_fixture,
    ) -> None:
        """
        Функция тестирует получение определенного подменю в рамках теста проверки количества блюд и подменю в меню.

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
            create_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание блюда,
            create_second_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание 2-ого
                                                          блюда,

        Returns:
            None
        """

        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        target_submenu_id = get_created_object_attribute(
            response=create_submenu_using_post_method_fixture, attribute='id'
        )

        target_dish_id = get_created_object_attribute(
            response=create_dish_using_post_method_fixture, attribute='id'
        )

        target_second_dish_id = get_created_object_attribute(
            response=create_second_dish_using_post_method_fixture, attribute='id'
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
                'dishes': [
                    {
                        'id': target_dish_id,
                        'title': DISH_TITLE_VALUE_TO_CREATE,
                        'description': DISH_DESCRIPTION_VALUE_TO_CREATE,
                        'price': str(DISH_PRICE_TO_CREATE),
                        'submenu_id': target_submenu_id,
                    },
                    {
                        'id': target_second_dish_id,
                        'title': SECOND_DISH_TITLE_VALUE_TO_CREATE,
                        'description': SECOND_DISH_DESCRIPTION_VALUE_TO_CREATE,
                        'price': str(SECOND_DISH_PRICE_TO_CREATE),
                        'submenu_id': target_submenu_id,
                    },
                ],
                'dishes_count': 2,
            },
        )

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        submenus_data = await get_specific_submenu_data_from_db()
        submenus_data_json = await submenus_data.json()
        submenus_data_json['dishes'] = await format_dishes(submenus_data_json['dishes'])

        assert submenus_data_json == response.json()


class TestDeleteSubmenu:
    @pytest.mark.asyncio
    async def test_delete_submenu_from_check_quan_of_dishes_and_submenus_method(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
    ) -> None:
        """
        Тест удаления подменю в рамках теста проверки количества блюд и подменю в меню.

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

        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

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
    async def test_get_submenus_method_after_delete_from_check_quan_of_dishes_and_submenus_method(
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


class TestGetDishesAfterDeleteSubmenu:
    @pytest.mark.asyncio
    async def test_get_dishes_method_after_delete_submenu_from_check_quan_of_dishes_and_submenus_method(
            self,
            ac: AsyncClient,
            create_menu_using_post_method_fixture: create_menu_using_post_method_fixture,
            create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
    ) -> None:
        """
        Тестирование события получения всех записей из таблицы dishes после удаления подменю, к которому блюда были
        привязаны.

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

        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        target_submenu_id = get_created_object_attribute(
            response=create_submenu_using_post_method_fixture, attribute='id'
        )

        url = dish_router.reverse(
            router_name='dish_get_method',
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id
        )

        response = await get_object_when_table_is_empty_internal_test(ac=ac, url=url)

        dishes_data = await get_dish_by_index(index=1)
        assert dishes_data == response.json()


class TestGetSpecificMenuAfterDeleteSubmenu:
    @pytest.mark.asyncio
    async def test_get_specific_menu_after_delete_submenu_with_dishes_from_check_quan_of_dishes_and_submenus_method(
            self, ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
    ) -> None:
        """
        Функция тестирует получение определенного меню после удаления подменю с блюдами.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. title найденной записи, которую вернул сервер, совпадает title'ом созданной ранее записи.
            3. description найденной записи, которую вернул сервер, совпадает description'ом созданной ранее записи.
            4. К меню не привязано подменю и блюда.

        Args:
            ac: клиент для асинхронных HTTP запросов.
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,

        Returns:
            None
        """

        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        url = menu_router.reverse(router_name='menu_base_url', target_menu_id=target_menu_id)

        response = await ac.get(url=url)

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


class TestDeleteMenu:
    @pytest.mark.asyncio
    async def test_delete_menu_from_check_quan_of_dishes_and_submenus_method(
            self, ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
    ) -> None:
        """
        Тест удаления меню.

        Тест проходит успешно, если:
            1. Код ответа 200.
            2. Тело ответа от сервера == {"status": "success!"}

        Args:
            ac: клиент для асинхронных HTTP запросов,
            create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,

        Returns:
            None
        """

        target_menu_id = get_created_object_attribute(
            response=create_menu_using_post_method_fixture, attribute='id'
        )

        url = menu_router.reverse(router_name='menu_base_url', target_menu_id=target_menu_id)

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

        url = '/api/v1/menus'

        response = await get_object_when_table_is_empty_internal_test(ac=ac, url=url)

        # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
        menus_data = await get_all_menus_data()

        assert menus_data == response.json()
