import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'superclave_secreta_para_flask')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://cesar:cesarc@isladigital.xyz:3311/f58_cesar')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('EMAIL_USER', 'davidsaavedrapinzon13@gmail.com')
    MAIL_PASSWORD = os.getenv('EMAIL_PASS', 'unxz cjlb vuwe ofzm')
    MAIL_DEFAULT_SENDER = os.getenv('EMAIL_USER', 'davidsaavedrapinzon13@gmail.com')
    
    # Tokens
    RESET_TOKEN_EXPIRATION = int(os.getenv('RESET_TOKEN_EXPIRATION', 3600))
    VERIFICATION_CODE_EXPIRATION = int(os.getenv('VERIFICATION_CODE_EXPIRATION', 600))

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}