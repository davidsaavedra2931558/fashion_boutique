import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Clave secreta para sesiones y tokens
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-por-defecto-cambiar-en-produccion'
    
    # Configuración de la base de datos (SQLite)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'fashion_boutique.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de Email con Gmail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    MAIL_DEFAULT_SENDER = os.environ.get('EMAIL_USER')
    
    # Tiempo de expiración para tokens y códigos (en segundos)
    RESET_TOKEN_EXPIRATION = 3600  # 1 hora
    VERIFICATION_CODE_EXPIRATION = 600  # 10 minutos
    
    # Google OAuth Configuration
    GOOGLE_OAUTH_CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
    GOOGLE_OAUTH_REDIRECT_URI = os.environ.get('GOOGLE_OAUTH_REDIRECT_URI') or 'http://localhost:5000/login/google/authorized'
    
    # Modo debug
    DEBUG = True