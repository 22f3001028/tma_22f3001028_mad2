from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
import redis
import os

db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()

redis_client = None

def init_redis(app):
    global redis_client
    try:
        redis_client = redis.from_url(app.config['REDIS_URL'], decode_responses=True)
        redis_client.ping()
        print("✅ Redis connected successfully")
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
        redis_client = None

def get_redis():
    return redis_client