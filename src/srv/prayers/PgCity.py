from app_types.stringable import AsyncSupportsStr, FkAsyncStr
from integrations.nominatim import NominatimCityName
from integrations.tg.coordinates import Coordinates
from srv.prayers.CityIdByName import CityIdByName
from srv.prayers.city import City


import attrs
from databases import Database
from pyeo import elegant


import uuid
from typing import final, override


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