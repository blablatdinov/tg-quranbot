# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from databases import Database

from app_types.listable import AsyncListable


@final
@attrs.define(frozen=True)
class PgCityNames(AsyncListable):
    """Имена городов из базы postgres."""

    _pgsql: Database
    _query: str

    @override
    async def to_list(self) -> list[str]:
        """Список строк.

        :returns: list[str]
        """
        search_query = '%{0}%'.format(self._query)
        db_query = '\n'.join([
            'SELECT name',
            'FROM cities',
            'WHERE name ILIKE :search_query',
            'LIMIT 20',
        ])
        return [
            row['name']
            for row in await self._pgsql.fetch_all(db_query, {'search_query': search_query})
        ]
