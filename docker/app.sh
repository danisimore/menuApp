#!/bin/bash

export PYTHONPATH=/fastapi_app/api_v1

alembic revision --autogenerate -m "Initial"
alembic upgrade head
gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000