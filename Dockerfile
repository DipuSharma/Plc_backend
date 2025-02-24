FROM python:3.12-alpine

WORKDIR /src

RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    make

RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the application port
EXPOSE 8000