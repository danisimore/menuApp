FROM python:3.10.12

RUN apt-get update && \
    apt-get install -y git


RUN mkdir /fastapi_app

WORKDIR /fastapi_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
RUN chmod +x docker/app.sh
#WORKDIR api_v1
#
#CMD gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000