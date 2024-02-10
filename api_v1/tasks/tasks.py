import asyncio
from celery import Celery
from google_sheets.data_sync import sync

broker_url = "amqp://localhost"
celery = Celery('tasks', broker=broker_url)


@celery.task
def sync_table_with_db():
    asyncio.run(sync())


celery.conf.beat_schedule = {
    'sync-every-15-seconds': {
        'task': 'tasks.sync_table_with_db',
        'schedule': 15.0,
    },
}
