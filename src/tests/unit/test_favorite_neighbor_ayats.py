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
import attrs
import pytest

from app_types.listable import AsyncListable
from repository.ayats.neighbor_ayats import FavoriteNeighborAyats
from srv.ayats.ayat import Ayat
from srv.ayats.ayat_identifier import AyatIdentifier


@attrs.define(frozen=True)
class FkIdentifier(AyatIdentifier):

    _id: int

    async def id(self):
        return self._id

    async def sura_num(self):
        return 1

    async def ayat_num(self):
        return '1-7'


@attrs.define(frozen=True)
class FkAyat(Ayat):

    _id: int

    def identifier(self):
        return FkIdentifier(self._id)

    async def text(self):
        return ''

    async def tg_file_id(self):
        return ''

    async def file_link(self):
        return ''


class FkFavoriteAyats(AsyncListable[Ayat]):

    async def to_list(self) -> list[Ayat]:
        return [
            FkAyat(1),
            FkAyat(2),
            FkAyat(3),
        ]


@pytest.mark.parametrize('ayat_id,expected', [
    (1, 'стр. 1/3'),
    (2, 'стр. 2/3'),
    (3, 'стр. 3/3'),
])
async def test_page(ayat_id, expected):
    got = await FavoriteNeighborAyats(
        ayat_id, FkFavoriteAyats(),
    ).page()

    assert got == expected
