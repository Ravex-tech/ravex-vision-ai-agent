import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "Ravex Vision AI Agent")
    APP_ENV = os.getenv("APP_ENV", "development")

    CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
    CAMERA_WIDTH = int(os.getenv("CAMERA_WIDTH", "1280"))
    CAMERA_HEIGHT = int(os.getenv("CAMERA_HEIGHT", "720"))
    CAMERA_FPS = int(os.getenv("CAMERA_FPS", "30"))

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()