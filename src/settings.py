# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import final

from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent  # Path to src dir


@final
class Settings(BaseSettings):  # noqa: PEO200
    """Настройки приложения."""

    REDIS_DSN: RedisDsn
    DEBUG: bool
    DATABASE_URL: PostgresDsn
    API_TOKEN: str
    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    RABBITMQ_HOST: str
    RABBITMQ_VHOST: str
    SENTRY_DSN: str
    ADMIN_CHAT_IDS: str
    TELEGRAM_CLIENT_ID: str = ''
    TELEGRAM_CLIENT_HASH: str = ''
    BASE_DIR: Path = BASE_DIR
    DAILY_AYATS: bool = False
    DAILY_PRAYERS: bool = False
    RAMADAN_MODE: bool = False
    PROMETHEUS_PORT: int = 9091

    def admin_chat_ids(self) -> list[int]:  # noqa: OVR100
        """Список идентификаторов админов.

        :return: list[int]
        """
        return [
            int(chat_id.strip())
            for chat_id in self.ADMIN_CHAT_IDS.strip().split(',')
        ]


env_file = BASE_DIR.parent / '.env'
settings = Settings(_env_file=env_file if env_file.exists() else None)
