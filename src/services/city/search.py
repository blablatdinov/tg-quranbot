from databases import Database
from loguru import logger
from pydantic import parse_obj_as

from exceptions.content_exceptions import CityNotSupportedError
from integrations.nominatim import GeoServiceIntegrationInterface
from repository.city import City


class SearchCityQueryInterface(object):

    def city_name(self):
        raise NotImplementedError

    def latitude(self):
        raise NotImplementedError

    def longitude(self):
        raise NotImplementedError


class SearchCityQuery(SearchCityQueryInterface):

    def __init__(
        self,
        *,
        string_query: tuple[str, ...] = tuple(),
        latitude: tuple[float, ...] = tuple(),
        longitude: tuple[float, ...] = tuple(),
    ):
        self._string_query = string_query
        self._latitude = latitude
        self._longitude = longitude

    @classmethod
    def from_string_cs(cls, query: str):
        return SearchCityQuery(string_query=(query,))

    @classmethod
    def from_coordinates_cs(cls, latitude: float, longitude: float):
        return SearchCityQuery(latitude=(latitude,), longitude=(longitude,))

    def city_name(self) -> str:
        if not self._string_query:
            raise AttributeError
        return self._string_query[0]

    def latitude(self):
        if not self._latitude:
            raise AttributeError
        return self._latitude[0]

    def longitude(self):
        if not self._longitude:
            raise AttributeError
        return self._longitude[0]


class CitySearchInterface(object):
    """Интерфейс для поиска городов."""

    async def search(self, query: SearchCityQueryInterface) -> list[City]:
        """Осуществить поиск.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class SearchCityByName(CitySearchInterface):
    """Поиск города по названию."""

    def __init__(self, db: Database):
        self._db = db

    async def search(self, query: SearchCityQueryInterface) -> list[City]:
        """Осуществить поиск.

        :returns: list[City]
        """
        search_query = '%{0}%'.format(query.city_name())
        query = 'SELECT city_id AS id, name FROM cities WHERE name ILIKE :search_query'
        rows = await self._db.fetch_all(query, {'search_query': search_query})
        return parse_obj_as(list[City], [row._mapping for row in rows])  # noqa: WPS437


class SearchCityByCoordinates(CitySearchInterface):
    """Поиск города по координатам."""

    def __init__(
        self,
        city_search: CitySearchInterface,
        geo_service_integration: GeoServiceIntegrationInterface,
    ):
        self._city_search = city_search
        self._geo_service_integration = geo_service_integration

    async def search(self, query: SearchCityQueryInterface) -> list[City]:
        """Осуществить поиск.

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
