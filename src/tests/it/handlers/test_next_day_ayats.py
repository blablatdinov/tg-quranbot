# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
import uuid

import pytest
import pytz
from sqlalchemy import text

from app_types.fk_update import FkUpdate
from handlers.next_day_ayats import NextDayAyats
from integrations.tg.tg_answers.fk_answer import FkAnswer


@pytest.fixture
async def _db_ayats(pgsql):
    file_ids = [str(uuid.uuid4()) for _ in range(10)]
    async with pgsql.connect() as conn:
        await conn.execute(
            text('\n'.join([
                'INSERT INTO files (file_id, telegram_file_id, link, created_at)',
                "VALUES (:file_id, 'aoiejf298jr9p23u8qr3', 'https://link-to-file.domain', :created_at)",
            ])),
            [
                {'file_id': file_id, 'created_at': datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))}
                for file_id in file_ids
            ],
        )
        await conn.execute(text('\n'.join([
            'INSERT INTO suras (sura_id, link) VALUES',
            "(2, '/link-to-sura')",
        ])))
        await conn.execute(
            text('\n'.join([
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
            ])),
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
        await conn.commit()


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
    async with pgsql.connect() as conn:
        assert (await conn.execute(text('SELECT day FROM users WHERE chat_id = 849375'))).scalar() == 4
