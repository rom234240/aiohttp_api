import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.environ.get('DATABASE_URL')
    JWT_SECRET = os.environ.get('JWT_SECRET', 'fallback_secret_change_in_production')
    JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')

    @classmethod
    def validate(cls):
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL is not set in environment variables")
        if not cls.JWT_SECRET or cls.JWT_SECRET == 'fallback_secret_change_in_production':
            raise ValueError("JWT_SECRET is not set or using default value")
