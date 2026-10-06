import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'tma-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'tma-jwt-secret-change-in-production')

    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'trekking.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TTL = 300

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'ovya4511@gmail.com'       # ← your Gmail address
    MAIL_PASSWORD = 'nwdx jxst zurq ndap'        # ← your 16-char app password
    MAIL_DEFAULT_SENDER = 'ovya4511@gmail.com' # ← same Gmail address
    ADMIN_EMAIL = 'ovya4511@gmail.com' 