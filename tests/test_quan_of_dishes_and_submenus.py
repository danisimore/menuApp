"""
Модуль для тестирования сценария проверки кол-ва блюд и подменю в меню.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 31 января 2024 | Добавлены тесты для сравнения запроса и данных из БД
"""

import pytest
from httpx import AsyncClient
from submenu.submenu_utils import format_dishes
from tests_services.dish_services_for_tests import get_dish_by_index
from tests_services.menu_services_for_tests import (
    get_all_menus_data,
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


@pytest.mark.asyncio
async def test_create_menu_from_check_quan_of_dishes_and_submenus_using_post_method(
        ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
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


@pytest.mark.asyncio
async def test_create_submenu_from_check_quan_of_dishes_and_submenus_using_post_method(
        ac: AsyncClient,
        create_submenu_using_post_method_fixture: create_submenu_using_post_method_fixture,
) -> None:
    """
    Тестирование создания подменю в рамках теста проверки количества блюд и подменю в меню.

    Тест проходит успешно, если:
        1. Код ответа 201.
        2. Данные из тела ответа соответствуют данным, переданным в запросе. Т.е. сервер вернул данные созданной записи
           и они соответствуют указанным.

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


@pytest.mark.asyncio
async def test_create_first_dish_from_check_quan_of_dishes_and_submenus_using_post_method(
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


@pytest.mark.asyncio
async def test_create_second_dish_from_check_quan_of_dishes_and_submenus_using_post_method(
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


@pytest.mark.asyncio
async def test_get_specific_menu_from_check_quan_of_dishes_and_submenus_method(
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
        create_second_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание 2-ого блюда,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(
        response=create_menu_using_post_method_fixture, attribute='id'
    )

    url = f'/api/v1/menus/{target_menu_id}'

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


@pytest.mark.asyncio
async def test_get_specific_submenu_from_check_quan_of_dishes_and_submenus_method(
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
        create_second_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание 2-ого блюда,

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

    # Получаем uuid, который вернул сервер после создания записи в таблице dishes с помощью фикстуры.
    target_second_dish_id = get_created_object_attribute(
        response=create_second_dish_using_post_method_fixture, attribute='id'
    )

    response = await ac.get(
        f'/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}'
    )

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
    submenus_data_json = submenus_data.json()
    # Преобразуем блюда к json, т.к. они хранятся в виде объектов
    submenus_data_json['dishes'] = await format_dishes(submenus_data_json['dishes'])

    assert submenus_data_json == response.json()


@pytest.mark.asyncio
async def test_delete_submenu_from_check_quan_of_dishes_and_submenus_method(
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

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(
        response=create_menu_using_post_method_fixture, attribute='id'
    )

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
    target_submenu_id = get_created_object_attribute(
        response=create_submenu_using_post_method_fixture, attribute='id'
    )

    await delete_object_internal_test(
        ac=ac, url=f'/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}'
    )

    # Проверяем, что для созданного меню действительно не существует подменю
    submenus_data = await get_submenus_data_from_db()
    assert submenus_data == []


@pytest.mark.asyncio
async def test_get_submenus_method_after_delete_from_check_quan_of_dishes_and_submenus_method(
        ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
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

    url = f'/api/v1/menus/{target_menu_id}/submenus'
    response = await get_object_when_table_is_empty_internal_test(ac=ac, url=url)

    # Проверяем, что для созданного меню действительно не существует подменю
    submenus_data = await get_submenus_data_from_db()
    assert submenus_data == response.json()


@pytest.mark.asyncio
async def test_get_dishes_method_after_delete_submenu_from_check_quan_of_dishes_and_submenus_method(
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

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(
        response=create_menu_using_post_method_fixture, attribute='id'
    )

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
    target_submenu_id = get_created_object_attribute(
        response=create_submenu_using_post_method_fixture, attribute='id'
    )

    url = f'/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes'

    response = await get_object_when_table_is_empty_internal_test(ac=ac, url=url)

    dishes_data = await get_dish_by_index(index=1)
    assert dishes_data == response.json()


@pytest.mark.asyncio
async def test_get_specific_menu_after_delete_submenu_with_dishes_from_check_quan_of_dishes_and_submenus_method(
        ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
) -> None:
    """
    Функция тестирует получение определенного меню после удаления подменю с блюдми.

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

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(
        response=create_menu_using_post_method_fixture, attribute='id'
    )

    url = f'/api/v1/menus/{target_menu_id}'

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


@pytest.mark.asyncio
async def test_delete_menu_from_check_quan_of_dishes_and_submenus_method(
        ac: AsyncClient, create_menu_using_post_method_fixture: create_menu_using_post_method_fixture
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

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(
        response=create_menu_using_post_method_fixture, attribute='id'
    )

    url = f'/api/v1/menus/{target_menu_id}'

    # Используем тест, который тестирует удаление записи.
    await delete_object_internal_test(ac=ac, url=url)

    # Проверяем, чтобы данные были удалены
    menus_data = await get_all_menus_data()
    assert menus_data == []


@pytest.mark.asyncio
async def test_get_menus_method_after_delete(ac: AsyncClient) -> None:
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
