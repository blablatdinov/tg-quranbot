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
import uuid

import pytest
import pytz

from app_types.fk_update import FkUpdate
from handlers.next_day_ayats import NextDayAyats
from integrations.tg.tg_answers.fk_answer import FkAnswer


@pytest.fixture
async def _db_ayats(pgsql):
    created_at = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    file_ids = [uuid.uuid4() for _ in range(10)]
    await pgsql.execute_many(
        '\n'.join([
            'INSERT INTO files (file_id, telegram_file_id, link, created_at)',
            "VALUES (:file_id, 'aoiejf298jr9p23u8qr3', 'https://link-to-file.domain', :created_at)",
        ]),
        [
            {'file_id': file_id, 'created_at': created_at}
            for file_id in file_ids
        ],
    )
    await pgsql.execute('\n'.join([
        'INSERT INTO suras (sura_id, link) VALUES',
        "(2, '/link-to-sura')",
    ]))
    await pgsql.execute_many(
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
        [
            {
                'ayat_id': ayat_id,
                'sura_id': 2,
                'public_id': str(uuid.uuid4()),
                'day': day,
                'ar_audio_id': file_id,
                'ayat_number': str(ayat_id),
                'content': '{0} day ayat content'.format(day),
                'arab_text': '',
                'transliteration': '',
            }
            for ayat_id, file_id, day in zip(
                range(1, 11),
                file_ids,
                [2 for _ in range(5)] + [3 for _ in range(5)],
                strict=True,
            )
        ],
    )


@pytest.fixture
async def _user(city_factory, user_factory):
    return await user_factory(
        849375,
        3,
        city=await city_factory(str(uuid.uuid4()), 'Kazan'),
    )


@pytest.mark.usefixtures('_db_ayats', '_user')
async def test(callback_update_factory, pgsql):
    got = await NextDayAyats(FkAnswer(), pgsql).build(
        FkUpdate(callback_update_factory(chat_id=849375)),
    )

    assert got[0].url.params['text'] == '\n'.join([
        '<b>2:6)</b> 3 day ayat content',
        '<b>2:7)</b> 3 day ayat content',
        '<b>2:8)</b> 3 day ayat content',
        '<b>2:9)</b> 3 day ayat content',
        '<b>2:10)</b> 3 day ayat content',
        '',
        'https://umma.ru/link-to-sura',
    ])
    assert got[0].url.params['chat_id'] == '849375'
    assert await pgsql.fetch_val('SELECT day FROM users WHERE chat_id = 849375') == 4
