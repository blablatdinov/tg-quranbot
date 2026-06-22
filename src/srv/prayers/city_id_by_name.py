# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app_types.async_supports_str import AsyncSupportsStr
from exceptions.content_exceptions import CityNotSupportedError


@final
@attrs.define(frozen=True)
class CityIdByName(AsyncSupportsStr):
    """Идентификатор города по имени."""

    _name: AsyncSupportsStr
    _pgsql: AsyncEngine

    @override
    async def to_str(self) -> str:
        """Строковое представление.

        :return: str
        :raises CityNotSupportedError: city not found
        """
        query = 'SELECT city_id FROM cities WHERE name = :name'
        async with self._pgsql.connect() as conn:
            query_result = await conn.execute(
                text(query),
                {'name': await self._name.to_str()},
            )
            row = query_result.fetchone()
        if row is None:
            raise CityNotSupportedError
        return row[0]
