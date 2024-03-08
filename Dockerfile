FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app

RUN --mount=type=cache,target=/root/.cache/pip \
    apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip3 install -r requirements.txt
