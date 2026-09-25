FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libxrender1 \
    libxext6 \
    libxtst6 \
    libxi6 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libgtk-3-0 \
    libgdk-pixbuf-2.0-0 \
    libxss1 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
