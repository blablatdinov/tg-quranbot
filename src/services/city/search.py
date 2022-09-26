from loguru import logger

from exceptions.content_exceptions import CityNotSupportedError
from integrations.nominatim import GeoServiceIntegrationInterface
from repository.city import City, CityRepositoryInterface


class CitySearchInterface(object):
    """Интерфейс для поиска городов."""

    async def search(self, query: str) -> list[City]:
        """Осуществить поиск.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class SearchCityByName(CitySearchInterface):
    """Поиск города по названию."""

    def __init__(self, city_service: CityRepositoryInterface):
        self._city_service = city_service

    async def search(self, query: str) -> list[City]:
        """Осуществить поиск.

        :returns: list[City]
        """
        return await self._city_service.search_by_name(query)


class SearchCityByCoordinates(CitySearchInterface):
    """Поиск города по координатам."""

    def __init__(
        self,
        city_service: CityRepositoryInterface,
        geo_service_integration: GeoServiceIntegrationInterface,
        latitude: str,
        longitude: str,
    ):
        self._city_service = city_service
        self._geo_service_integration = geo_service_integration
        self._latitude = latitude
        self._longitude = longitude

    async def search(self) -> list[City]:
        """Осуществить поиск.

        :returns: list[City]
        :raises CityNotSupportedError: если город не найден в БД
        """
        city_name = await self._geo_service_integration.search(self._latitude, self._longitude)
        logger.info('Search city {0} in DB'.format(city_name))
        cities = await self._city_service.search_by_name(city_name)
        logger.info('Finded cities: {0}'.format(cities))
        if not cities:
            template = 'Для города {0} я не знаю времен намазов, пожалуйста напишите моему разработчику'
            raise CityNotSupportedError(template.format(city_name))
        return cities
