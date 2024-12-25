# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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
from srv.prayers.city import City
from srv.prayers.fk_city import FkCity
from srv.users.pg_user import PgUser
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


@pytest.fixture
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


@pytest.fixture
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
            '(ayat_id, sura_id, public_id, day, ar_audio_id, ayat_number, content, arab_text, transliteration)',
            'VALUES',
            '(',
            '  :ayat_id,',
            '  :sura_id,',
            '  :public_id,',
            '  :day,',
            '  :ar_audio_id,',
            '  :ayat_number,',
            '  :content,',
            '  :arab_text,',
            '  :transliteration',
            ')',
        ]),
        {
            'ayat_id': 1,
            'sura_id': 1,
            'public_id': '3067bdc4-8dc0-456b-aa68-e38122b5f2f8',
            'day': 1,
            'ar_audio_id': '82db206b-34ed-4ae0-ac83-1f0c56dfde90',
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


@pytest.fixture
def city_factory(pgsql):
    async def _city_factory(city_id, name):  # noqa: WPS430
        await pgsql.execute(
            'INSERT INTO cities (city_id, name) VALUES (:city_id, :city_name)',
            {'city_id': city_id, 'city_name': name},
        )
        return FkCity(city_id, name)
    return _city_factory


@pytest.fixture
def user_factory(pgsql):
    async def _user_factory(  # noqa: WPS430
        chat_id,
        day=2,
        city: City | None = None,
        legacy_id: int | None = None,
        is_active: bool = True,
    ):  # noqa: WPS430
        await pgsql.execute(
            '\n'.join([
                'INSERT INTO users (chat_id, day, city_id, is_active, legacy_id) VALUES',
                '(:chat_id, :day, :city_id, :is_active, :legacy_id)',
            ]),
            {
                'chat_id': chat_id,
                'day': day or 2,
                'city_id': await city.city_id() if city else None,
                'legacy_id': legacy_id or None,
                'is_active': is_active,
            },
        )
        return PgUser.int_ctor(chat_id, pgsql)
    return _user_factory


@pytest.fixture
async def prayers_factory(pgsql, city_factory, user_factory):
    city = await city_factory('080fd3f4-678e-4a1c-97d2-4460700fe7ac', 'Kazan')
    await user_factory(905, city=city)

    async def _prayers_factory(date_as_str):  # noqa: WPS430
        query = '\n'.join([
            'INSERT INTO prayers (prayer_id, name, "time", city_id, day) VALUES',
            "(1, 'fajr', '05:43:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '{0}'),",
            "(2, 'sunrise', '08:02:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '{0}'),",
            "(3, 'dhuhr', '12:00:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '{0}'),",
            "(4, 'asr', '13:21:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '{0}'),",
            "(5, 'maghrib', '15:07:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '{0}'),",
            "(6, 'isha''a', '17:04:00', '080fd3f4-678e-4a1c-97d2-4460700fe7ac', '{0}')",
        ]).format(date_as_str)
        await pgsql.execute(query)
    return _prayers_factory
