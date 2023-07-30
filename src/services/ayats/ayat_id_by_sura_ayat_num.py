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
from pyeo import elegant
from typing import final

import attrs
from databases import Database

from app_types.intable import AsyncIntable
from exceptions.content_exceptions import AyatNotFoundError
from repository.ayats.sura import AyatStructure, SuraInterface
from services.ayats.search.ayat_search_query import SearchQueryInterface


@final
@attrs.define(frozen=True)
@elegant
class AyatIdBySuraAyatNum(AsyncIntable):
    """Поиск аятов по номеру суры, аята."""

    _sura: SuraInterface
    _query: SearchQueryInterface
    _database: Database

    async def to_int(self) -> int:
        """Числовое представление.

        :return: int
        :raises AyatNotFoundError: если аят не найден
        """
        ayat_num = self._query.ayat()
        ayats = await self._sura.ayats(self._query.sura())
        for ayat in ayats:
            ayat_id = self._search_in_sura_ayats(ayat, ayat_num)
            if ayat_id:
                return ayat_id
        raise AyatNotFoundError

    def _search_in_sura_ayats(self, ayat: AyatStructure, ayat_num: str) -> int | None:
        if '-' in ayat.ayat_num:
            return self._service_range_case(ayat, ayat_num)
        elif ',' in ayat.ayat_num:
            return self._service_comma_case(ayat, ayat_num)
        elif ayat.ayat_num == ayat_num:
            return ayat.id
        return None

    def _service_range_case(self, ayat: AyatStructure, ayat_num: str) -> int | None:
        left, right = map(int, ayat.ayat_num.split('-'))
        if int(ayat_num) in range(left, right + 1):
            return ayat.id
        return None

    def _service_comma_case(self, ayat: AyatStructure, ayat_num: str) -> int | None:
        left, right = map(int, ayat.ayat_num.split(','))
        if int(ayat_num) in range(left, right + 1):
            return ayat.id
        return None
