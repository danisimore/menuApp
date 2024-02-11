"""
Модуль реализующий функционал синхронизации Гугл таблиц с БД

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru

Дата: 11 февраля 2024
"""

import asyncio

from exceptions import CustomException
from operations import (
    clear_tables,
    create_dish_using_data_from_sheets,
    create_menu_using_data_from_sheets,
    create_submenu_using_data_from_sheets,
)
from services import create_cache, delete_cache_by_key, get_cache
from tasks.tasks import get_sheets_data


async def sync_table(sheets_response: list[list[str]]) -> None:
    """
    Синхронизирует данные из таблицы Google Sheets с данными в БД.

    Исходя из структуры таблицы получаем данные вида:
        1.
            [
                [
                    'Номер_меню',
                    'Название_меню',
                    'Описание_меню'
                ],
                [
                    '',
                    'Номер_подменю',
                    'Название_подменю',
                    'Описание_подменю'
                ],
                [
                    '',
                    '',
                    'Номер_блюда',
                    'Название_блюда',
                    'Описание_блюда',
                    'Цена_блюда',
                    'Скидка'
                ]
                ....
            ]

    :param sheets_response: данные из таблицы
    :return: None
    """

    for value_list in sheets_response:
        if len(value_list) == 3:
            target_menu_id = await create_menu_using_data_from_sheets(menu_data_from_table=value_list)

        elif len(value_list) == 4:
            try:
                target_submenu_id = await create_submenu_using_data_from_sheets(
                    submenu_data_from_table=value_list,
                    target_menu_id=target_menu_id
                )
            except UnboundLocalError:
                await delete_cache_by_key(key='table_cache')
                raise CustomException(
                    message='Check the correctness of the data in the Google Sheet!',
                    extra_info='The menu was expected to be created'
                )

        elif len(value_list) in [6, 7]:
            await create_dish_using_data_from_sheets(
                dish_data_from_table=value_list,
                target_submenu_id=target_submenu_id
            )


async def sync() -> None:
    """
    Запускает синхронизацию и проверяет наличие изменений в таблице

    :return: None
    """

    while True:
        cache = await get_cache(key='table_cache')

        result = get_sheets_data.delay()
        table_data = result.get()

        try:
            data_values = table_data['valueRanges'][0]['values']

            if cache == data_values:
                print('В таблице ничего не изменилось. Изменения не были внесены!')
            else:
                await clear_tables()
                await create_cache(key='table_cache', value=data_values)
                await sync_table(sheets_response=data_values)

                print('Изменения были внесены!')

        except KeyError:
            if cache == table_data['valueRanges'][0]:
                print('В таблице ничего не изменилось. Изменения не были внесены!')
            else:
                await clear_tables()

                await create_cache(key='table_cache', value=table_data['valueRanges'][0])

                print('Изменения были внесены!')

        await asyncio.sleep(15)


asyncio.run(sync())
