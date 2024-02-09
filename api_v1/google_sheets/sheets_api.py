import os
from typing import Any

import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


def get_service_sacc() -> None:
    """
    Создает объект сервиса Google Sheets API

    :return: None
    """
    creds_json = os.path.dirname(__file__) + "/y_lab_mentor_key.json"
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)


def get_table_data() -> dict[Any, Any]:
    """
    Получает данные из гугл таблицы

    :return: ответ Google Sheets
    """

    sheet_id = '1hhrwkP1xBU7jvxVEcwtBVkSOhLEwJBG3ZpOiA0D-hfY'
    response = get_service_sacc().spreadsheets().values().batchGet(spreadsheetId=sheet_id, ranges=["Лист1"]).execute()

    return response
