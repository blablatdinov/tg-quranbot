# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime

import pytest
import pytz

from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.fk_text_search_query import FkTextSearchQuery
from srv.ayats.text_search_neighbor_ayats import TextSearchNeighborAyats


@pytest.fixture
async def _db_ayat(pgsql):
    created_at = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    await pgsql.execute_many(
        '\n'.join([
            'INSERT INTO files (file_id, telegram_file_id, link, created_at)',
            "VALUES (:file_id, 'aoiejf298jr9p23u8qr3', 'https://link-to-file.domain', :created_at)",
        ]),
        [
            {'file_id': '82db206b-34ed-4ae0-ac83-1f0c56dfde90', 'created_at': created_at},
            {'file_id': '99cce289-cfa0-4f92-8c3b-84aac82814ba', 'created_at': created_at},
        ],
    )
    await pgsql.execute('\n'.join([
        'INSERT INTO suras (sura_id, link) VALUES',
        "(1, 'https://link-to-sura.domain'),",
        "(2, 'https://link-to-sura.domain')",
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
            {
                'ayat_id': 2,
                'sura_id': 2,
                'public_id': '3067bdc4-8dc0-456b-aa68-e38122b5f2f8',
                'day': 1,
                'ar_audio_id': '82db206b-34ed-4ae0-ac83-1f0c56dfde90',
                'ayat_number': '1-5',
                'content': 'Content',
                'arab_text': 'Arab text',
                'transliteration': 'Transliteration',
            },
            {
                'ayat_id': 3,
                'sura_id': 2,
                'public_id': '3067bdc4-8dc0-456b-aa68-e38122b5f2f8',
                'day': 1,
                'ar_audio_id': '82db206b-34ed-4ae0-ac83-1f0c56dfde90',
                'ayat_number': '6,7',
                'content': 'Content',
                'arab_text': 'Arab text',
                'transliteration': 'Transliteration',
            },
        ],
    )


@pytest.mark.usefixtures('_db_ayat')
async def test_search_first(pgsql):
    neighbor = TextSearchNeighborAyats.ctor(pgsql, 1, FkTextSearchQuery('Content'))

    with pytest.raises(AyatNotFoundError):
        await neighbor.left_neighbor()
    assert await (await neighbor.right_neighbor()).identifier().ayat_id() == 2
    assert await neighbor.page() == 'стр. 1/3'


@pytest.mark.usefixtures('_db_ayat')
async def test_search_last(pgsql):
    neighbor = TextSearchNeighborAyats.ctor(pgsql, 3, FkTextSearchQuery('Content'))

    with pytest.raises(AyatNotFoundError):
        await neighbor.right_neighbor()
    assert await (await neighbor.left_neighbor()).identifier().ayat_id() == 2
    assert await neighbor.page() == 'стр. 3/3'
