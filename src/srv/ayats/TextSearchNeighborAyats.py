from typing import final, override

import attrs
from databases import Database
from pyeo import elegant

from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.ayat import Ayat
from srv.ayats.neighbor_ayats import NeighborAyats
from srv.ayats.pg_ayat import PgAyat
from srv.ayats.text_len_shorten_ayat import TextLenSafeAyat
from srv.ayats.text_search_query import TextSearchQuery


@final
@attrs.define(frozen=True)
@elegant
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
            if row['ayat_id'] == self._ayat_id:
                return TextLenSafeAyat(
                    PgAyat.from_int(rows[idx - 1]['ayat_id'], self._pgsql),
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
            if row['ayat_id'] == self._ayat_id:
                return TextLenSafeAyat(
                    PgAyat.from_int(rows[idx + 1]['ayat_id'], self._pgsql),
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
            if row['ayat_id'] == self._ayat_id:
                actual_page_num = idx
        return 'стр. {0}/{1}'.format(actual_page_num, len(rows))
