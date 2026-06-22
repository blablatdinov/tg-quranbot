# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from typing import final, override

import attrs
from furl import furl
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app_types.async_supports_str import AsyncSupportsStr
from exceptions.internal_exceptions import CityNotFoundError
from srv.prayers.city import City


@final
@attrs.define(frozen=True)
class HgPrayersUrl(AsyncSupportsStr):
    """Url, по которому можно посмотреть время намаза для города на сайте https://halalguide.me .

    Пример: https://halalguide.me/kazan/namaz-time/june-2025
    """

    _city: City
    _pgsql: AsyncEngine
    _date: datetime.date

    @override
    async def to_str(self) -> str:
        """Строковое представление."""
        async with self._pgsql.connect() as conn:
            result = await conn.execute(
                text('SELECT link FROM halal_guide_cities WHERE city_id = :city_id'),
                {'city_id': str(await self._city.city_id())},
            )
            row = result.fetchone()
        if row is None:
            raise CityNotFoundError
        link = row[0]
        return str(
            furl(link) / '{0}-{1}'.format(
                self._date.strftime('%B').lower(),
                self._date.year,
            ),
        )
