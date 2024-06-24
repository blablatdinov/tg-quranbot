# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

import datetime

import psycopg2
import pytest
import pytz
from databases import Database

from settings import BASE_DIR, Settings
from srv.ayats.fk_ayat import FkAyat
from srv.ayats.fk_identifier import FkIdentifier
from srv.files.fk_file import FkFile
from tests.creating_test_db import apply_migrations, create_db, drop_db


@pytest.fixture(scope='session')
def _migrate():
    create_db()
    connection = psycopg2.connect(
        str(Settings(_env_file=BASE_DIR.parent / '.env').DATABASE_URL),
    )
    connection.autocommit = True
    cursor = connection.cursor()
    apply_migrations(cursor)
    connection.close()
    yield
    drop_db()


@pytest.fixture()
async def pgsql(_migrate):
    db_url = str(Settings(_env_file=BASE_DIR.parent / '.env').DATABASE_URL)
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
async def db_ayat(pgsql):
    created_at = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    await pgsql.execute(
        '\n'.join([
            'INSERT INTO files (file_id, telegram_file_id, link, created_at)',
            "VALUES (:file_id, 'aoiejf298jr9p23u8qr3', 'https://link-to-file.domain', :created_at)",
        ]),
        {'file_id': '82db206b-34ed-4ae0-ac83-1f0c56dfde90', 'created_at': created_at},
    )
    await pgsql.execute('\n'.join([
        'INSERT INTO suras (sura_id, link) VALUES',
        "(1, '/link-to-sura')",
    ]))
    await pgsql.execute(
        '\n'.join([
            'INSERT INTO ayats',
            '(ayat_id, sura_id, public_id, day, audio_id, ayat_number, content, arab_text, transliteration)',
            'VALUES',
            '(:ayat_id, :sura_id, :public_id, :day, :audio_id, :ayat_number, :content, :arab_text, :transliteration)',
        ]),
        {
            'ayat_id': 1,
            'sura_id': 1,
            'public_id': '3067bdc4-8dc0-456b-aa68-e38122b5f2f8',
            'day': 1,
            'audio_id': '82db206b-34ed-4ae0-ac83-1f0c56dfde90',
            'ayat_number': '1-7',
            'content': 'Content',
            'arab_text': 'Arab text',
            'transliteration': 'Transliteration',
        },
    )
    return FkAyat(
        FkIdentifier(1, 1, '1-7'),
        '',
        FkFile('', ''),
    )


@pytest.fixture()
async def _prayers(pgsql):
    await pgsql.execute("INSERT INTO cities (city_id, name) VALUES ('080fd3f4-678e-4a1c-97d2-4460700fe7ac', 'Kazan')")
    await pgsql.execute("INSERT INTO users (chat_id, city_id) VALUES (905, '080fd3f4-678e-4a1c-97d2-4460700fe7ac')")
    query = '\n'.join([
        'INSERT INTO prayers (prayer_id, name, "time", city_id, day) VALUES',
        "(1, 'fajr', '05:43:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '2023-12-19'),",
        "(2, 'sunrise', '08:02:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '2023-12-19'),",
        "(3, 'dhuhr', '12:00:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '2023-12-19'),",
        "(4, 'asr', '13:21:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '2023-12-19'),",
        "(5, 'maghrib', '15:07:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '2023-12-19'),",
        "(6, 'isha''a', '17:04:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '2023-12-19')",
    ])
    await pgsql.execute(query)
