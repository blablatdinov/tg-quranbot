"""The MIT License (MIT).

Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

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
import datetime
import uuid

import pytest

from exceptions.content_exceptions import BotFileNotFoundError
from srv.files.pg_file import PgFile


@pytest.fixture()
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
        'created_at': datetime.datetime.now(),
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
