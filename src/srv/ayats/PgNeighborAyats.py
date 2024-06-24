from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.ayat import Ayat
from srv.ayats.neighbor_ayats import NeighborAyats
from srv.ayats.pg_ayat import PgAyat
from srv.ayats.text_len_shorten_ayat import TextLenSafeAyat


import attrs
from databases import Database
from pyeo import elegant


from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class PgNeighborAyats(NeighborAyats):
    """Класс для работы с соседними аятами в хранилище."""

    _pgsql: Database
    _ayat_id: int

    @override
    async def left_neighbor(self) -> Ayat:
        """Получить левый аят.

        :return: AyatShort
        :raises AyatNotFoundError: if ayat not found
        """
        query = '\n'.join([
            'SELECT ayat_id',
            'FROM ayats',
            'WHERE ayat_id = :ayat_id',
        ])
        row = await self._pgsql.fetch_one(query, {'ayat_id': self._ayat_id - 1})
        if not row:
            raise AyatNotFoundError
        return TextLenSafeAyat(PgAyat.from_int(row['ayat_id'], self._pgsql))

    @override
    async def right_neighbor(self) -> Ayat:
        """Получить правый аят.

        :return: AyatShort
        :raises AyatNotFoundError: if ayat not found
        """
        query = '\n'.join([
            'SELECT ayats.ayat_id',
            'FROM ayats',
            'WHERE ayats.ayat_id = :ayat_id',
        ])
        row = await self._pgsql.fetch_one(query, {'ayat_id': self._ayat_id + 1})
        if not row:
            raise AyatNotFoundError
        return TextLenSafeAyat(PgAyat.from_int(row['ayat_id'], self._pgsql))

    @override
    async def page(self) -> str:
        """Информация о странице.

        :return: str
        """
        ayats_count = await self._pgsql.fetch_val('SELECT COUNT(*) FROM ayats')
        actual_page_num = await self._pgsql.fetch_val(
            'SELECT COUNT(*) FROM ayats WHERE ayat_id <= :ayat_id',
            {'ayat_id': self._ayat_id},
        )
        return 'стр. {0}/{1}'.format(actual_page_num, ayats_count)