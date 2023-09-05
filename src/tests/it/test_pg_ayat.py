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
import datetime

import pytest
from eljson.json_doc import JsonDoc

from srv.ayats.pg_ayat import PgAyat


@pytest.fixture()
async def db_ayat(pgsql):
    await pgsql.execute_many(
        '\n'.join([
            'INSERT INTO files (file_id, telegram_file_id, link, created_at)',
            "VALUES (:file_id, 'aoiejf298jr9p23u8qr3', 'https://link-to-file.domain', :created_at)",
        ]),
        [
            {'file_id': '82db206b-34ed-4ae0-ac83-1f0c56dfde90', 'created_at': datetime.datetime.now()},
            {'file_id': '99cce289-cfa0-4f92-8c3b-84aac82814ba', 'created_at': datetime.datetime.now()},
        ],
    )
    await pgsql.execute(
        '\n'.join([
            'INSERT INTO suras (sura_id, link)',
            "VALUES (1, 'https://link-to-sura.domain')",
        ]),
    )
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
            'content': 'Ayat content',
            'arab_text': 'Arab text',
            'transliteration': 'Transliteration',
        },
    )


async def test_change(db_ayat, pgsql):
    event = {
        'event_id': 'some_id',
        'event_version': 1,
        'event_name': 'event_name',
        'event_time': '392409283',
        'producer': 'some producer',
        'data': {
            'public_id': '3067bdc4-8dc0-456b-aa68-e38122b5f2f8',
            'day': 2,
            'audio_id': '99cce289-cfa0-4f92-8c3b-84aac82814ba',
            'ayat_number': '1-3',
            'content': 'Updated content',
            'arab_text': 'Updated arab text',
            'transliteration': 'Updated arab transliteration',
        },
    }
    await PgAyat.ayat_changed_event_ctor(JsonDoc(event), pgsql).change(JsonDoc(event))

    changed_record = await pgsql.fetch_one('SELECT * FROM ayats WHERE ayat_id = 1')

    assert dict(changed_record._mapping) == {  # noqa: WPS437
        'arab_text': 'Updated arab text',
        'audio_id': '99cce289-cfa0-4f92-8c3b-84aac82814ba',
        'ayat_id': 1,
        'ayat_number': '1-3',
        'content': 'Updated content',
        'day': 2,
        'public_id': '3067bdc4-8dc0-456b-aa68-e38122b5f2f8',
        'sura_id': 1,
        'transliteration': 'Updated arab transliteration',
    }