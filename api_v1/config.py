"""
Модуль для получения значений переменных окружения.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 25 января 2024 | Добавлена загрузка переменных окружения для тестовой БД
"""

import os

from dotenv import load_dotenv

load_dotenv("/home/danisimore/Desktop/dev/restaurant_menu/.env-example")

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")


TEST_DB_USER = os.environ.get("TEST_DB_USER")
TEST_DB_PASSWORD = os.environ.get("TEST_DB_PASSWORD")
TEST_DB_NAME = os.environ.get("TEST_DB_NAME")
TEST_DB_HOST = os.environ.get("TEST_DB_HOST")
TEST_DB_PORT = os.environ.get("TEST_DB_PORT")
