#!/bin/bash

export PYTHONPATH=/fastapi_app/api_v1

cd api_v1

celery -A tasks.tasks worker --loglevel=INFO --detach
celery -A tasks.tasks beat --loglevel=INFO --detach

cd sync_google_sheets

python3 data_sync.py
