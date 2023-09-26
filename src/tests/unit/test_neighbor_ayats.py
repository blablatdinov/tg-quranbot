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
from exceptions.base_exception import BaseAppError
from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.ayat import Ayat
from srv.ayats.ayat_identifier import AyatIdentifier
from srv.ayats.neighbor_ayats import FavoriteNeighborAyats
from srv.files.file import FkFile, TgFile


@attrs.define(frozen=True)
class FkIdentifier(AyatIdentifier):

    _id: int
    _sura_num: int
    _ayat_num: str

    async def id(self):
        return self._id

    async def sura_num(self):
        return self._sura_num

    async def ayat_num(self):
        return self._ayat_num


@attrs.define(frozen=True)
class FkAyat(Ayat):

    _id: AyatIdentifier
    _text: str
    _audio: TgFile

    def identifier(self):
        return self._id

    async def text(self):
        return self._text

    async def audio(self):
        return self._audio


@attrs.define(frozen=True)
class FkAyatsList(AsyncListable):

    _ayats: list[FkAyat]

    async def to_list(self) -> list[FkAyat]:
        return self._ayats


@pytest.fixture()
def neighbor():
    def _neighbor(ayat_id: int, *ctor_args):
        return FavoriteNeighborAyats(
            ayat_id,
            FkAyatsList([
                FkAyat(*ctor)
                for ctor in ctor_args
            ]),
        )
    return _neighbor


async def test_first(neighbor):
    neighbor_ayats = neighbor(
        1,
        (FkIdentifier(1, 1, '1-7'), '', FkFile('', '')),
        (FkIdentifier(2, 2, '1-5'), '', FkFile('', '')),
        (FkIdentifier(3, 2, '6, 7'), '', FkFile('', '')),
    )

    with pytest.raises(AyatNotFoundError):
        await neighbor_ayats.left_neighbor()
    right_neighbor = await neighbor_ayats.right_neighbor()
    assert await right_neighbor.identifier().id() == 2
    assert await neighbor_ayats.page() == 'стр. 1/3'


async def test_middle(neighbor):
    neighbor_ayats = neighbor(
        2,
        (FkIdentifier(1, 1, '1-7'), '', FkFile('', '')),
        (FkIdentifier(2, 2, '1-5'), '', FkFile('', '')),
        (FkIdentifier(3, 2, '6, 7'), '', FkFile('', '')),
    )

    assert await neighbor_ayats.page() == 'стр. 2/3'


async def test_last(neighbor):
    neighbor_ayats = neighbor(
        3,
        (FkIdentifier(1, 1, '1-7'), '', FkFile('', '')),
        (FkIdentifier(2, 2, '1-5'), '', FkFile('', '')),
        (FkIdentifier(3, 2, '6, 7'), '', FkFile('', '')),
    )

    with pytest.raises(AyatNotFoundError):
        await neighbor_ayats.right_neighbor()
    right_neighbor = await neighbor_ayats.left_neighbor()
    assert await right_neighbor.identifier().id() == 2
    assert await neighbor_ayats.page() == 'стр. 3/3'


async def test_empty(neighbor):
    neighbor_ayats = neighbor(1)

    with pytest.raises(AyatNotFoundError):
        await neighbor_ayats.right_neighbor()
    with pytest.raises(AyatNotFoundError):
        await neighbor_ayats.left_neighbor()
    with pytest.raises(BaseAppError):
        await neighbor_ayats.page()
