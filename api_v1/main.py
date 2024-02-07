"""
Модуль для подключения роутеров к приложению fastapi.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 06 февраля 2024
"""
import json

from dish.router import router as dish_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from menu.router import router as menu_router
from submenu.router import router as submenu_router

app = FastAPI(title='Restaurant Menu')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def custom_openapi() -> None:
    """
    Заменяет дефолтный json для openapi на кастомный

    :return: None
    """
    if app.openapi_schema:
        return app.openapi_schema
    with open('/home/danisimore/Desktop/menu_app/pythonProject/api_v1/docs/openapi.json') as file:
    # with open('/fastapi_app/api_v1/docs/openapi.json') as file:
        openapi_schema = json.loads(file.read())

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get('/health')
async def read_health():
    return {'status': 'OK'}

app.include_router(menu_router)
app.include_router(submenu_router)
app.include_router(dish_router)
