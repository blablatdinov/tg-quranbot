"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
from pathlib import Path
from typing import Optional, final
from urllib.parse import urljoin

import sentry_sdk
from pydantic import BaseSettings, HttpUrl, RedisDsn

BASE_DIR = Path(__file__).parent


@final
class Settings(BaseSettings):
    """Класс с настройками."""

    BASE_DIR: Path = BASE_DIR
    API_TOKEN: str
    COMMIT_HASH: str = 'unknown'
    DATABASE_URL: str
    TEST_DATABASE_URL: str = ''
    SENTRY_DSN: Optional[HttpUrl] = None
    DEBUG: bool
    REDIS_DSN: RedisDsn
    ADMIN_CHAT_IDS: list[int] = [358610865]
    WEBHOOK_HOST: str = 'https://quranbot.ilaletdinov.ru'
    WEBHOOK_PATH: str = '/bot'
    WEBAPP_HOST: str = 'localhost'
    WEBAPP_PORT: int = 8010
    NATS_HOST: str = 'localhost'
    NATS_PORT: int = 4222
    NATS_TOKEN: str

    @property
    def webhook_url(self) -> str:
        """Путь для приема пакетов от телеграма.

        :return: str
        """
        return urljoin(self.WEBHOOK_HOST, self.WEBHOOK_PATH)

    @property
    def alembic_db_url(self) -> str:
        """Формирование адреса подключения к БД для алембика.

        :return: str
        """
        uri = self.DATABASE_URL
        if self.DATABASE_URL and self.DATABASE_URL.startswith('postgres://'):
            uri = self.DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        return uri.replace('postgresql', 'postgresql+asyncpg')

    class Config(object):
        """Конфигурация настроек."""

        env_file = '.env'


settings = Settings()

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
    )
