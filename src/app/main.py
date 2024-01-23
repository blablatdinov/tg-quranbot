"""The MIT License (MIT).

Copyright (c) 2013-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

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
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import psycopg2
from litestar import Litestar, get
from litestar.datastructures import State
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    pgsql_dsn: PostgresDsn

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()


@asynccontextmanager
async def db_connection(app: Litestar) -> AsyncIterator[None]:
    """Connection to postgres database.

    :param app: Litestar
    :yields: None
    """
    engine = getattr(app, 'db_conn', None)
    if not engine:
        with psycopg2.connect(str(settings.pgsql_dsn)) as conn:
            app.state.db_conn = conn
    yield


@get('/healthcheck')
def healthcheck(state: State) -> dict:
    """Healthcheck endpoint.

    :param state: State
    :return: dict
    """
    start = time.time()
    with state.db_conn.cursor() as curr:
        curr.execute('SELECT 1')
        db_query_time = time.time() - start
    return {
        'app': 'ok',
        'db': round(db_query_time, 3),
    }


app = Litestar([healthcheck], lifespan=[db_connection])
