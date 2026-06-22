# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app_types.listable import AsyncListable


@final
@attrs.define(frozen=True)
class PgCityNames(AsyncListable):
    """Имена городов из базы postgres."""

    _pgsql: AsyncEngine
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
        async with self._pgsql.connect() as conn:
            query_result = await conn.execute(text(db_query), {'search_query': search_query})
            rows = query_result.fetchall()
        return [
            dict(row)['name']
            for row in rows
        ]
