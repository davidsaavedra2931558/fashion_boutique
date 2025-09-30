FROM python:3.13-alpine

# FIX: Dockerfile renamed from dockerfile
RUN apk add --no-cache mariadb-connector-c-dev \
    && apk add --no-cache --virtual .build-deps build-base mariadb-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apk del .build-deps

COPY . .
EXPOSE 5000
CMD ["python", "run.py"]