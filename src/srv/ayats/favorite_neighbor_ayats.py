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

# flake8: noqa: WPS232

from typing import final, override

import attrs
from pyeo import elegant

from app_types.listable import AsyncListable
from exceptions.base_exception import BaseAppError
from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.ayat import Ayat
from srv.ayats.neighbor_ayats import NeighborAyats


@final
@attrs.define(frozen=True)
@elegant
class FavoriteNeighborAyats(NeighborAyats):
    """Класс для работы с соседними аятами в хранилище."""

    _ayat_id: int
    _favorite_ayats: AsyncListable[Ayat]

    @override
    async def left_neighbor(self) -> Ayat:
        """Получить левый аят.

        :return: Ayat
        :raises AyatNotFoundError: if ayat not found
        """
        fav_ayats = await self._favorite_ayats.to_list()
        for ayat_index, ayat in enumerate(fav_ayats):
            ayat_id = await ayat.identifier().ayat_id()
            if ayat_id == self._ayat_id and ayat_index == 0:
                raise AyatNotFoundError
            if ayat_id == self._ayat_id:
                return fav_ayats[ayat_index - 1]
        raise AyatNotFoundError

    @override
    async def right_neighbor(self) -> Ayat:
        """Получить правый аят.

        :return: AyatShort
        :raises AyatNotFoundError: if ayat not found
        """
        fav_ayats = await self._favorite_ayats.to_list()
        for ayat_index, ayat in enumerate(fav_ayats):
            ayat_id = await ayat.identifier().ayat_id()
            if ayat_id == self._ayat_id and ayat_index + 1 == len(fav_ayats):
                raise AyatNotFoundError
            if ayat_id == self._ayat_id:
                return fav_ayats[ayat_index + 1]
        raise AyatNotFoundError

    @override
    async def page(self) -> str:
        """Информация о странице.

        :return: str
        :raises BaseAppError: if page not generated
        """
        fav_ayats = await self._favorite_ayats.to_list()
        for ayat_idx, ayat in enumerate(fav_ayats, start=1):
            if self._ayat_id == 1:
                return 'стр. 1/{0}'.format(len(fav_ayats))
            if await ayat.identifier().ayat_id() == len(fav_ayats):
                return 'стр. {0}/{0}'.format(len(fav_ayats))
            if self._ayat_id == await ayat.identifier().ayat_id():
                return 'стр. {0}/{1}'.format(ayat_idx, len(fav_ayats))
        msg = 'Page info not generated'
        raise BaseAppError(msg)
