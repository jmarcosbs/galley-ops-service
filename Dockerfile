# syntax=docker/dockerfile:1

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY . /app

RUN apt-get update \
    && apt-get install -y xmlsec1 \
    && rm -rf /var/lib/apt/lists/*

RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]