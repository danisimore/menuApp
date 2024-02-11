"""
Модуль с реализацией Celery задач.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 11 февраля 2024
"""
from typing import Any

from celery import Celery
from google_sheets.sheets_api import get_table_data

broker_url = 'amqp://localhost'
result_backend = 'rpc://'
celery = Celery('tasks', broker=broker_url, backend=result_backend)


@celery.task
def get_sheets_data() -> dict[Any, Any]:
    """
    Таска для получения данных из Google Sheets.

    :return: dict - ответ Google Sheets API
    """

    response = get_table_data()

    return response


celery.conf.beat_schedule = {
    'sync-every-15-seconds': {
        'task': 'tasks.tasks.get_sheets_data',
        'schedule': 15.0,
    },
}
