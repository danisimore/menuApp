from conftest import async_session_maker
from menu.menu_services import select_all_menus, select_specific_menu
from submenu.submenu_services import select_all_submenus, select_specific_submenu


async def get_submenu_data_from_db():
    # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
    async with async_session_maker() as session:
        # Т.к. menu в рамках теста одно, мы можем получить его id, для того чтобы тестирование БД и Response были
        # независимы
        menus_data = await select_all_menus(session=session)
        menus_data_json = menus_data[0].json()
        menu_id_in_db = menus_data_json["id"]

        submenus = await select_all_submenus(session=session, target_menu_id=menu_id_in_db)

        try:
            submenus_json = submenus[0].json()

            return [submenus_json]
        except IndexError:
            return []


async def get_specific_submenu_data_from_db():
    # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
    async with async_session_maker() as session:
        # Т.к. menu в рамках теста одно, мы можем получить его id, для того чтобы тестирование БД и Response были
        # независимы
        menus_data = await select_all_menus(session=session)
        menus_data_json = menus_data[0].json()
        menu_id_in_db = menus_data_json["id"]

        # Т.к. submenu в рамках теста одно, мы можем получить его id, для того чтобы тестирование БД и Response были
        # независимы
        submenus_data = await select_all_submenus(session=session, target_menu_id=menu_id_in_db)
        try:
            submenus_data_json = submenus_data[0].json()
            submenu_id_in_db = submenus_data_json["id"]

            submenu = await select_specific_submenu(
                session=session,
                target_menu_id=menu_id_in_db,
                target_submenu_id=submenu_id_in_db
            )

            return submenu
        except IndexError:
            return {'detail': 'submenu not found'}
