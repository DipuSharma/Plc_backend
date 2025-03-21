import os
import pathlib
from pathlib import Path
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()


# @lru_cache()
class Settings:
    TAGS = [
        {"name": "Auth", "description": "This is Authentication Routes"},
    ]
    DEBUG = os.getenv("DEBUG")
    PASS = os.getenv("PASS")
    TITLE = "Plc Application"
    NAME = "Dipu Kumar Sharma"
    ALGORITHM = os.getenv("ALGO")
    PROJECT_VERSION: str = "1.0.0"
    HOST_URL = os.getenv("HOST_URL")
    HOST_PORT = os.getenv("HOST_PORT")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS").split(",")
    HOST_MAIN_URL = f"{HOST_URL}:{HOST_PORT}"
    BASE_DIR = Path(__file__).resolve().parent
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mongodb://mongodb:27018")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "plc_data")

    MQTT_BROKER = os.getenv("MQTT_BROKER")
    MQTT_PORT: int = os.getenv("MQTT_PORT")
    MQTT_TOPIC = os.getenv("MQTT_TOPIC")


setting = Settings()
