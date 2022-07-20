from pathlib import Path
from urllib.parse import urljoin

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
    WEBHOOK_HOST: str = 'https://quranbot.ilaletdinov.ru'
    WEBHOOK_PATH: str = '/bot'
    WEBAPP_HOST: str = 'localhost'
    WEBAPP_PORT: int = 8010

    @property
    def webhook_url(self) -> str:
        """Путь для приема пакетов от телеграма.

        :return: str
        """
        return urljoin(self.WEBHOOK_HOST, self.WEBHOOK_PATH)

    class Config(object):
        """Конфигурация настроек."""

        env_file = '.env'


settings = Settings()
