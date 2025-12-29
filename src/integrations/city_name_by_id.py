# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import TypeAlias, final, override

import attrs
from databases import Database

from app_types.async_supports_str import AsyncSupportsStr
from exceptions.content_exceptions import CityNotSupportedError

CityName: TypeAlias = AsyncSupportsStr


@final
@attrs.define(frozen=True)
class CityNameById(CityName):
    """Имя города по id."""

    _pgsql: Database
    _city_id: AsyncSupportsStr

    @override
    async def to_str(self) -> str:
        """Поиск.

        :return: str
        :raises CityNotSupportedError: City not found
        """
        city_name = await self._pgsql.fetch_val('SELECT name FROM cities WHERE city_id = :city_id', {
            'city_id': await self._city_id.to_str(),
        })
        if not city_name:
            raise CityNotSupportedError
        return city_name
