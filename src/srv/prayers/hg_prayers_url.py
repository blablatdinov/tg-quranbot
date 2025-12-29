# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from typing import final, override

import attrs
from databases import Database
from furl import furl

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
    _pgsql: Database
    _date: datetime.date

    @override
    async def to_str(self) -> str:
        """Строковое представление."""
        link = await self._pgsql.fetch_val(
            'SELECT link FROM halal_guide_cities WHERE city_id = :city_id',
            {'city_id': str(await self._city.city_id())},
        )
        if not link:
            raise CityNotFoundError
        return str(
            furl(link) / '{0}-{1}'.format(
                self._date.strftime('%B').lower(),
                self._date.year,
            ),
        )
