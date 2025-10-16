FROM python:3.13-alpine

# Definir directorio de trabajo
WORKDIR /app

# Copiar dependencias primero (para aprovechar la cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Exponer el puerto de Flask
EXPOSE 5000

# Comando por defecto
CMD ["python", "run.py"]
