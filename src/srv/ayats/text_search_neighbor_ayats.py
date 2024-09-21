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

from typing import Final, final, override

import attrs
from databases import Database

from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.ayat import Ayat
from srv.ayats.neighbor_ayats import NeighborAyats
from srv.ayats.pg_ayat import PgAyat
from srv.ayats.text_len_shorten_ayat import TextLenSafeAyat
from srv.ayats.text_search_query import TextSearchQuery

_AYAT_ID_LITERAL: Final = 'ayat_id'


@final
@attrs.define(frozen=True)
class TextSearchNeighborAyats(NeighborAyats):
    """Класс для работы с сосденими аятами, при текстовом поиске."""

    _pgsql: Database
    _ayat_id: int
    _query: TextSearchQuery
    _search_sql_query = '\n'.join([
        'SELECT ayats.ayat_id',
        'FROM ayats',
        'WHERE ayats.content ILIKE :search_query',
        'ORDER BY ayats.ayat_id',
    ])

    @override
    async def left_neighbor(self) -> Ayat:
        """Получить левый аят.

        :return: AyatShort
        :raises AyatNotFoundError: if ayat not found
        """
        search_query = '%{0}%'.format(await self._query.read())
        rows = await self._pgsql.fetch_all(self._search_sql_query, {'search_query': search_query})
        for idx, row in enumerate(rows[1:], start=1):
            if row[_AYAT_ID_LITERAL] == self._ayat_id:
                return TextLenSafeAyat(
                    PgAyat.from_int(rows[idx - 1][_AYAT_ID_LITERAL], self._pgsql),
                )
        raise AyatNotFoundError

    @override
    async def right_neighbor(self) -> Ayat:
        """Получить правый аят.

        :return: AyatShort
        :raises AyatNotFoundError: if ayat not found
        """
        search_query = '%{0}%'.format(await self._query.read())
        rows = await self._pgsql.fetch_all(self._search_sql_query, {'search_query': search_query})
        for idx, row in enumerate(rows[:-1]):
            if row[_AYAT_ID_LITERAL] == self._ayat_id:
                return TextLenSafeAyat(
                    PgAyat.from_int(rows[idx + 1][_AYAT_ID_LITERAL], self._pgsql),
                )
        raise AyatNotFoundError

    @override
    async def page(self) -> str:
        """Информация о странице.

        :return: str
        """
        actual_page_num = 0
        rows = await self._pgsql.fetch_all(
            self._search_sql_query,
            {'search_query': '%{0}%'.format(await self._query.read())},
        )
        for idx, row in enumerate(rows, start=1):
            if row[_AYAT_ID_LITERAL] == self._ayat_id:
                actual_page_num = idx
        return 'стр. {0}/{1}'.format(actual_page_num, len(rows))
