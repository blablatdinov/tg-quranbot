# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from collections.abc import Sequence
from typing import final, override

import attrs
from databases import Database

from app_types.fk_async_int import FkAsyncInt
from app_types.listable import AsyncListable
from app_types.stringable import SupportsStr
from srv.ayats.ayat import Ayat
from srv.ayats.pg_ayat import PgAyat
from srv.ayats.text_len_shorten_ayat import TextLenSafeAyat


@final
@attrs.define(frozen=True)
class AyatsByTextQuery(AsyncListable):
    """Список аятов, найденных по текстовому запросу."""

    _query: SupportsStr
    _pgsql: Database

    @override
    async def to_list(self) -> Sequence[Ayat]:
        """Список.

        :return: list[QAyat]
        """
        query = '\n'.join([
            'SELECT a.ayat_id AS id',
            'FROM ayats AS a',
            'WHERE a.content ILIKE :search_query',
            'ORDER BY a.ayat_id',
        ])
        rows = await self._pgsql.fetch_all(query, {
            'search_query': '%{0}%'.format(self._query),
        })
        return [
            TextLenSafeAyat(
                PgAyat(
                    FkAsyncInt(row['id']),
                    self._pgsql,
                ),
            )
            for row in rows
        ]
