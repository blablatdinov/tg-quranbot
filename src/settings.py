from pathlib import Path

from pydantic import BaseSettings

BASE_DIR = Path(__file__).parent


class Settings(BaseSettings):
    """Класс с настройками."""

    BASE_DIR: Path = BASE_DIR
    API_TOKEN: str
    DATABASE_URL: str
    DEBUG: bool
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_DB: int = 5
    ADMIN_CHAT_IDS: list[int] = [358610865]

    class Config(object):
        """Конфигурация настроек."""

        env_file = '.env'


settings = Settings()
