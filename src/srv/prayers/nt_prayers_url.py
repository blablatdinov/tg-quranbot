# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from databases import Database

from app_types.async_supports_str import AsyncSupportsStr
from exceptions.internal_exceptions import CityNotFoundError
from srv.prayers.city import City


@final
@attrs.define(frozen=True)
class NtPrayersUrl(AsyncSupportsStr):
    """Url, по которому можно посмотреть время намаза для города на сайте https://namaz.today .

    Пример: https://namaz.today/city/kazan
    """

    _city: City
    _pgsql: Database

    @override
    async def to_str(self) -> str:
        """Строковое представление."""
        link = await self._pgsql.fetch_val(
            'SELECT link FROM namaz_today_cities WHERE city_id = :city_id',
            {'city_id': str(await self._city.city_id())},
        )
        if not link:
            raise CityNotFoundError
        return link
