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
from typing import final

import pytest
from pyeo import elegant

from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from repository.ayats.neighbor_ayats import FavoriteNeighborAyats
from repository.ayats.schemas import Ayat


@elegant
@final
class FavoriteAyatRepositoryFake(FavoriteAyatRepositoryInterface):

    async def get_favorite(self, ayat_id: int) -> Ayat:
        raise NotImplementedError

    async def check_ayat_is_favorite_for_user(self, ayat_id: int, chat_id: int) -> bool:
        raise NotImplementedError

    async def get_favorites(self, chat_id: int) -> list[Ayat]:
        return [
            Ayat(
                id=1,
                sura_num=1,
                ayat_num='2',
                arab_text='',
                content='',
                transliteration='',
                sura_link='',
                audio_telegram_id='',
                link_to_audio_file='',
            ),
            Ayat(
                id=2,
                sura_num=1,
                ayat_num='2',
                arab_text='',
                content='',  # noqa: WPS110 wrong variable name
                transliteration='',
                sura_link='',
                audio_telegram_id='',
                link_to_audio_file='',
            ),
            Ayat(
                id=3,
                sura_num=1,
                ayat_num='2',
                arab_text='',
                content='',  # noqa: WPS110 wrong variable name
                transliteration='',
                sura_link='',
                audio_telegram_id='',
                link_to_audio_file='',
            ),
        ]


@pytest.mark.parametrize('ayat_id,expected', [
    (1, 'стр. 1/3'),
    (2, 'стр. 2/3'),
    (3, 'стр. 3/3'),
])
async def test_page(ayat_id, expected):
    got = await FavoriteNeighborAyats(
        ayat_id, 1, FavoriteAyatRepositoryFake(),
    ).page()

    assert got == expected
