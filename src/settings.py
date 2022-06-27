from pathlib import Path

from pydantic import BaseSettings

BASE_DIR = Path(__file__).parent


class Settings(BaseSettings):
    """Класс с настройками."""

    BASE_DIR: Path = BASE_DIR
    API_TOKEN: str
    DATABASE_URL: str

    class Config(object):
        """Конфигурация настроек."""

        env_file = '.env'


settings = Settings()
