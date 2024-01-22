#!/bin/bash

export PYTHONPATH=/fastapi_app/api_v1

sleep 10

mkdir -p /fastapi_app/alembic/versions

alembic revision --autogenerate -m "Initial"
alembic upgrade head
gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000