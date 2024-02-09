import json
import aiohttp


async def fetch_data(url, data):
    async with aiohttp.ClientSession() as session:
        headers = {'Content-Type': 'application/json'}
        async with session.post(url=url, data=json.dumps(data), headers=headers) as post_response:
            return await post_response.text()


async def delete_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.delete(url=url) as delete_response:
            return await delete_response.text()


async def clear_tables():
    await delete_data(url='ttp://localhost:8000/api/v1/menus/delete_all_records')


async def create_menu_using_post_method_and_table_data(menu_data_from_table):
    cntr = 0
    menu_data = {}

    for data in menu_data_from_table:
        if cntr == 1:
            menu_data["title"] = data
        elif cntr == 2:
            menu_data["description"] = data
            resp = await fetch_data(url='http://localhost:8000/api/v1/menus', data=menu_data)
            resp_json = json.loads(resp)
            target_menu_id = resp_json['id']

            return target_menu_id

        cntr += 1


async def create_submenu_using_post_method_and_table_data(submenu_data_from_table, target_menu_id):
    cntr = 0
    submenu_data = {}
    for data in submenu_data_from_table:
        if cntr == 2:
            submenu_data['title'] = data
        elif cntr == 3:
            submenu_data['description'] = data
            resp = await fetch_data(
                url=f'http://localhost:8000/api/v1/menus/{target_menu_id}/submenus',
                data=submenu_data
            )

            resp_json = json.loads(resp)
            target_submenu_id = resp_json['id']

            return target_submenu_id

        cntr += 1


async def create_dish_using_post_method_and_table_data(dish_data_from_table, target_menu_id, target_submenu_id):
    cntr = 0
    dish_data = {}

    for data in dish_data_from_table:
        if cntr == 3:
            dish_data['title'] = data
        elif cntr == 4:
            dish_data['description'] = data
        elif cntr == 5:
            formatted_price = data.replace(',', '.')
            dish_data['price'] = formatted_price
            resp = await fetch_data(
                url=f'http://localhost:8000/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes',
                data=dish_data
            )
            resp_json = json.loads(resp)

            return resp_json
        cntr += 1
