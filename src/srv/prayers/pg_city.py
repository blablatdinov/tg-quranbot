# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import uuid
from typing import final, override

import attrs
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app_types.async_supports_str import AsyncSupportsStr
from app_types.fk_async_str import FkAsyncStr
from exceptions.internal_exceptions import CityNotFoundError
from integrations.nominatim_city_name import NominatimCityName
from integrations.tg.coordinates import Coordinates
from integrations.tg.fk_chat_id import ChatId
from srv.prayers.city import City
from srv.prayers.city_id_by_name import CityIdByName
from srv.prayers.user_city_id import UserCityId


@final
@attrs.define(frozen=True)
class PgCity(City):
    """Город в БД postgres."""

    _city_id: AsyncSupportsStr
    _pgsql: AsyncEngine

    @classmethod
    def name_ctor(cls, city_name: str, pgsql: AsyncEngine) -> City:
        """Конструктор для имени города.

        :param city_name: str
        :param pgsql: AsyncEngine
        :return: City
        """
        return cls(CityIdByName(FkAsyncStr(city_name), pgsql), pgsql)

    @classmethod
    def location_ctor(cls, location: Coordinates, pgsql: AsyncEngine) -> City:
        """Конструктор для координат города.

        :param location: Coordinates
        :param pgsql: AsyncEngine
        :return: City
        """
        return cls(CityIdByName(NominatimCityName(location), pgsql), pgsql)

    @classmethod
    def user_ctor(cls, user_id: ChatId, pgsql: AsyncEngine) -> City:
        """Конструктор для идентификатора пользователя."""
        return cls(UserCityId(pgsql, user_id), pgsql)

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
        async with self._pgsql.connect() as conn:
            result = await conn.execute(
                text(query),
                {'city_id': await self._city_id.to_str()},
            )
            row = result.fetchone()
        if row is None:
            raise CityNotFoundError
        return row[0]
