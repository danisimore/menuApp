from sqlalchemy import select, cast, Boolean


async def is_submenu_in_target_menu(
    submenu, target_menu_id, session, target_submenu_id
):
    # Формируем запрос для нахождения всех подменю, которые привязаны к меню с id равным target_menu_id.
    stmt_submenus_linked_to_target_menu_id = select(submenu).where(
        cast(submenu.menu_id == target_menu_id, Boolean)
    )
    # Исполняем запрос.
    result_submenus_linked_to_target_menu_id = await session.execute(
        stmt_submenus_linked_to_target_menu_id
    )
    # Получаем список найденных объектов (Подменю, привязанных к target_menu_id).
    submenus_linked_to_target_menu_id = (
        result_submenus_linked_to_target_menu_id.scalars().all()
    )

    if submenus_linked_to_target_menu_id:
        for submenu in submenus_linked_to_target_menu_id:
            if str(submenu.id) == target_submenu_id:
                return True

    return False
