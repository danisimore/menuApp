from conftest import async_session_maker
from menu.menu_services import select_all_menus, select_specific_menu


async def get_all_menus_data_from_empty_table():
    async with async_session_maker() as session:
        menu_data = await select_all_menus(session=session)

        return menu_data


async def get_all_menus_data_from_table_with_data():
    # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
    async with async_session_maker() as session:
        menus_data = await select_all_menus(session=session)

        # Т.к. в рамках теста запись одна, получаем ее из списка и преобразовываем ее uuid
        menus_data_json = menus_data[0].json()
        menus_data_json["id"] = str(menus_data_json["id"])

        return [menus_data_json]


async def get_menu_data_from_db_without_counters():
    # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
    async with async_session_maker() as session:
        # Получаем все меню.
        menus_data = await select_all_menus(session=session)
        # Т.к. оно одно, забираем первое и преобразуем в json.
        menu_data_json = menus_data[0].json()

        # Преобразуем UUID в строку для корректного сравнения
        menu_data_json["id"] = str(menu_data_json["id"])

        return menu_data_json


async def get_menu_data_from_db_with_counters():
    # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
    async with async_session_maker() as session:
        # Т.к. menu в рамках теста одно, мы можем получить его id, для того чтобы тестирование БД и Response были
        # независимы
        menus_data = await select_all_menus(session=session)
        menus_data_json = menus_data[0].json()
        menu_id_in_db = str(menus_data_json["id"])

        # Здесь будет кортеж со списком вида [(<MENU OBJECT>, submenus_count, dishes_count)]
        menus_with_counts = await select_specific_menu(session=session, target_menu_id=menu_id_in_db)

        if menus_with_counts:
            menu = menus_with_counts[0][0]
            menu.submenus_count = menus_with_counts[0][1]
            menu.dishes_count = menus_with_counts[0][2]

            menu.id = str(menu.id)

            return menu.json()
