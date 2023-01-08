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
from typing import Union, final

from exceptions.content_exceptions import AyatNotFoundError
from repository.ayats.schemas import Ayat
from repository.ayats.sura import SuraInterface
from services.ayats.ayat_search_interface import AyatSearchInterface
from services.ayats.search.ayat_search_query import SearchQuery, ValidatedSearchQuery


@final
class AyatBySuraAyatNum(AyatSearchInterface):
    """Поиск аята по номеру суры, аята."""

    def __init__(self, sura: SuraInterface):
        """Конструктор класса.

        :param sura: SuraInterface
        """
        self._sura = sura

    async def search(self, search_query: Union[str, int]) -> Ayat:
        """Поиск аята.

        :param search_query: Union[str, int]
        :return: list[httpx.Request]
        :raises AyatNotFoundError: if ayat not found
        :raises TypeError: if search query has int type
        """
        if isinstance(search_query, int):
            raise TypeError
        query = ValidatedSearchQuery(
            SearchQuery(search_query),
        )
        ayat_num = query.ayat()
        ayats = await self._sura.ayats(query.sura())
        for ayat in ayats:
            result_ayat = self._search_in_sura_ayats(ayat, ayat_num)
            if result_ayat:
                return result_ayat[0]
        raise AyatNotFoundError

    def _search_in_sura_ayats(self, ayat: Ayat, ayat_num: str) -> tuple[Ayat, ...]:
        result_ayat: tuple[Ayat, ...] = ()
        if '-' in ayat.ayat_num:
            result_ayat = self._service_range_case(ayat, ayat_num)
        elif ',' in ayat.ayat_num:
            result_ayat = self._service_comma_case(ayat, ayat_num)
        elif ayat.ayat_num == ayat_num:
            result_ayat = (ayat,)
        return result_ayat

    def _service_range_case(self, ayat: Ayat, ayat_num: str) -> tuple[Ayat, ...]:
        left, right = map(int, ayat.ayat_num.split('-'))
        if int(ayat_num) in range(left, right + 1):
            return (ayat,)
        return ()

    def _service_comma_case(self, ayat: Ayat, ayat_num: str) -> tuple[Ayat, ...]:
        left, right = map(int, ayat.ayat_num.split(','))
        if int(ayat_num) in range(left, right + 1):
            return (ayat,)
        return ()
