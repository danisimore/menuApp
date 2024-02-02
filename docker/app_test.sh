#!/bin/bash

export PYTHONPATH=/fastapi_app/api_v1
export ENV_FILE=/fastapi_app/.env-example

sleep 5

gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8001
