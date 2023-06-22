"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
from typing import Protocol, final

import attrs
from databases import Database
from loguru import logger
from pydantic import parse_obj_as

from exceptions.content_exceptions import CityNotSupportedError
from integrations.nominatim import GeoServiceIntegrationInterface
from repository.city import City


class SearchCityQueryInterface(Protocol):
    """Интерфейс поискового запроса городов."""

    def city_name(self) -> str:
        """Имя города."""

    def latitude(self) -> float:
        """Ширина города."""

    def longitude(self) -> float:
        """Долгота города."""


@final
@attrs.define
class SearchCityQuery(SearchCityQueryInterface):
    """Запрос для поиска города."""

    _string_query: tuple[str, ...] = ()
    _latitude: tuple[float, ...] = ()
    _longitude: tuple[float, ...] = ()

    @classmethod
    def from_string_cs(cls, query: str):
        """Конструктор для строкового запроса.

        :param query: str
        :return: SearchCityQuery
        """
        return SearchCityQuery(string_query=(query,))

    @classmethod
    def from_coordinates_cs(cls, latitude: float, longitude: float):
        """Конструктор для запроса по координатам.

        :param latitude: float
        :param longitude: float
        :return: SearchCityQuery
        """
        return SearchCityQuery(latitude=(latitude,), longitude=(longitude,))

    def city_name(self) -> str:
        """Имя города.

        :return: str
        :raises AttributeError: Если запрос собран по координатам
        """
        if not self._string_query:
            raise AttributeError
        return self._string_query[0]

    def latitude(self):
        """Широта города.

        :return: float
        :raises AttributeError: Если запрос собран по имени города
        """
        if not self._latitude:
            raise AttributeError
        return self._latitude[0]

    def longitude(self):
        """Долгота города.

        :return: float
        :raises AttributeError: Если запрос собран по имени города
        """
        if not self._longitude:
            raise AttributeError
        return self._longitude[0]


class CitySearchInterface(Protocol):
    """Интерфейс для поиска городов."""

    async def search(self, query: SearchCityQueryInterface) -> list[City]:
        """Осуществить поиск.

        :param query: SearchCityQueryInterface
        """


@final
@attrs.define
class SearchCityByName(CitySearchInterface):
    """Поиск города по названию."""

    _db: Database

    async def search(self, query: SearchCityQueryInterface) -> list[City]:
        """Осуществить поиск.

        :param query: SearchCityQueryInterface
        :returns: list[City]
        """
        search_query = '%{0}%'.format(query.city_name())
        db_query = 'SELECT city_id AS id, name FROM cities WHERE name ILIKE :search_query'
        rows = await self._db.fetch_all(db_query, {'search_query': search_query})
        return parse_obj_as(list[City], [row._mapping for row in rows])  # noqa: WPS437


@final
@attrs.define
class SearchCityByCoordinates(CitySearchInterface):
    """Поиск города по координатам."""

    _city_search: CitySearchInterface
    _geo_service_integration: GeoServiceIntegrationInterface

    async def search(self, query: SearchCityQueryInterface) -> list[City]:
        """Осуществить поиск.

        :param query: SearchCityQueryInterface
        :returns: list[City]
        :raises CityNotSupportedError: если город не найден в БД
        """
        city_name = await self._geo_service_integration.search(
            str(query.latitude()),
            str(query.longitude()),
        )
        logger.info('Search city {0} in DB'.format(city_name))
        cities = await self._city_search.search(
            SearchCityQuery.from_string_cs(city_name),
        )
        logger.info('Finded cities: {0}'.format(cities))
        if not cities:
            template = 'Для города {0} я не знаю времен намазов, пожалуйста напишите моему разработчику'
            raise CityNotSupportedError(template.format(city_name))
        return cities
