# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
import uuid

import pytest
import pytz

from exceptions.content_exceptions import BotFileNotFoundError
from srv.files.pg_file import PgFile


@pytest.fixture
async def db_file_id(pgsql):
    file_id = uuid.uuid4()
    query = '\n'.join([
        'INSERT INTO files (file_id, telegram_file_id, link, created_at)',
        'VALUES (:file_id, :tg_file_id, :link, :created_at)',
    ])
    await pgsql.execute(query, {
        'file_id': str(file_id),
        'tg_file_id': 'adsf',
        'link': 'https://link.domain',
        'created_at': datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')),
    })
    return file_id


async def test(pgsql, db_file_id):
    pg_file = PgFile(db_file_id, pgsql)

    assert await pg_file.tg_file_id() == 'adsf'
    assert await pg_file.file_link() == 'https://link.domain'


async def test_not_found(pgsql):
    pg_file = PgFile(uuid.uuid4(), pgsql)

    with pytest.raises(BotFileNotFoundError):
        await pg_file.tg_file_id()
    with pytest.raises(BotFileNotFoundError):
        await pg_file.file_link()
