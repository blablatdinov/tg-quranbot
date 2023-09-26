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
import psycopg2
import pytest
import redis
from databases import Database

from settings import EnvFileSettings
from tests.creating_test_db import apply_migrations, create_db, drop_db


@pytest.fixture(scope='session')
def migrate():
    create_db()
    connection = psycopg2.connect(EnvFileSettings.from_filename('../.env').DATABASE_URL)
    connection.autocommit = True
    cursor = connection.cursor()
    apply_migrations(cursor)
    connection.close()
    yield
    drop_db()


@pytest.fixture(scope='function')
async def pgsql(migrate):
    db_url = EnvFileSettings.from_filename('../.env').DATABASE_URL
    database = Database(db_url)
    await database.connect()
    yield database
    tables = (
        'prayers_at_user',
        'favorite_ayats',
        'podcast_reactions',
        'podcasts',
        'users',
        'prayers',
        'cities',
        'ayats',
        'suras',
        'files',
        'admin_messages',
    )
    for table in tables:
        await database.execute('DELETE FROM {0}'.format(table))  # noqa: S608
    await database.execute("SELECT setval('podcasts_podcast_id_seq', 1, false)")
    await database.execute("SELECT setval('prayers_at_user_prayer_at_user_id_seq', 1, false)")
    await database.disconnect()


@pytest.fixture()
async def rds():
    rd = redis.asyncio.from_url(EnvFileSettings.from_filename('../.env').REDIS_DSN)
    yield rd
    await rd.close()
