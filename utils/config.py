import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    TITLE = os.getenv("TITLE", "Training Provider API")
    DESCRIPTION = os.getenv("VERSION", "FastAPI for a generic Training Provider App")
    VERSION = os.getenv("VERSION", "0.9")
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
    REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "your_refresh_secret")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    ACCESS_LIMIT = os.getenv("ACCESS_LIMIT", "10000/seconds")
    MAX_GET_LIMIT = os.getenv("MAX_GET_LIMIT", "10000")
    DEFAULT_GET_LIMIT = os.getenv("DEFAULT_GET_LIMIT", "1000")


settings = Settings()
