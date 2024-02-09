import asyncio


from sheets_api import get_table_data
from repsonses import (
    create_menu_using_post_method_and_table_data,
    create_submenu_using_post_method_and_table_data,
    create_dish_using_post_method_and_table_data,
    clear_tables
)
from services import create_cache, get_cache


async def parse_table(sheets_response):
    for value_list in sheets_response:
        if len(value_list) == 3:
            target_menu_id = await create_menu_using_post_method_and_table_data(menu_data_from_table=value_list)
        elif len(value_list) == 4:
            target_submenu_id = await create_submenu_using_post_method_and_table_data(
                submenu_data_from_table=value_list,
                target_menu_id=target_menu_id
            )
        elif len(value_list) == 6:
            await create_dish_using_post_method_and_table_data(
                dish_data_from_table=value_list,
                target_menu_id=target_menu_id,
                target_submenu_id=target_submenu_id
            )


async def get_result():
    cache = await get_cache(key="table_cache")

    table_data = get_table_data()

    try:
        data_values = table_data["valueRanges"][0]["values"]
    except KeyError:
        await clear_tables()

        return 'Данные синхронизацированы!'

    if cache == data_values:
        return "В таблице ничего не изменилось. Изменения не были внесены!"
    else:
        await clear_tables()
        await create_cache(key="table_cache", value=data_values)
        await parse_table(sheets_response=data_values)

        return "Изменения были внесены!"


asyncio.run(get_result())
