FROM python:3.13-alpine

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar requirements.txt e instalar dependencias
COPY requirements.txt .
RUN apk update \
    && apk add --no-cache --virtual .build-deps gcc musl-dev \
    && pip install --default-timeout=100 --no-cache-dir -r requirements.txt \
    && apk del .build-deps

# Copiar el resto del código
COPY . .

EXPOSE 5000

CMD [ "python", "run.py" ]
#CMD sh -c "gunicorn --bind 0.0.0.0:8081 --workers 4 --forwarded-allow-ips=*  wsgi:app"