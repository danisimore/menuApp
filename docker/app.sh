#!/bin/bash

export PYTHONPATH=/fastapi_app/api_v1
export ENV_FILE=/fastapi_app/.env-prod

sleep 10

alembic upgrade head
gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000