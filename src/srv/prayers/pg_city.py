# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

import uuid
from typing import final, override

import attrs
from databases import Database
from pyeo import elegant

from app_types.async_supports_str import AsyncSupportsStr
from app_types.fk_async_str import FkAsyncStr
from integrations.nominatim_city_name import NominatimCityName
from integrations.tg.coordinates import Coordinates
from srv.prayers.city import City
from srv.prayers.city_id_by_name import CityIdByName


@final
@attrs.define(frozen=True)
@elegant
class PgCity(City):
    """Город в БД postgres."""

    _city_id: AsyncSupportsStr
    _pgsql: Database

    @classmethod
    def name_ctor(cls, city_name: str, pgsql: Database) -> City:
        """Конструктор для имени города.

        :param city_name: str
        :param pgsql: Database
        :return: City
        """
        return cls(CityIdByName(FkAsyncStr(city_name), pgsql), pgsql)

    @classmethod
    def location_ctor(cls, location: Coordinates, pgsql: Database) -> City:
        """Конструктор для координат города.

        :param location: Coordinates
        :param pgsql: Database
        :return: City
        """
        return cls(CityIdByName(NominatimCityName(location), pgsql), pgsql)

    @override
    async def city_id(self) -> uuid.UUID:
        """Идентификатор города.

        :return: uuid.UUID
        """
        return uuid.UUID(await self._city_id.to_str())

    @override
    async def name(self) -> str:
        """Имя города.

        :return: str
        """
        query = 'SELECT name FROM cities WHERE city_id = :city_id'
        return await self._pgsql.fetch_val(
            query,
            {'city_id': await self._city_id.to_str()},
        )
