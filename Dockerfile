FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y git


RUN mkdir /fastapi_app

WORKDIR /fastapi_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
RUN chmod +x docker/app.sh
