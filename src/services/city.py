from dataclasses import dataclass

from aiogram import types

from answerable import Answerable
from exceptions import UserHasNotCityIdError
from integrations.nominatim import GeoServiceIntegrationInterface
from repository.city import City, CityRepositoryInterface
from services.answer import Answer, AnswerInterface


class CityService(object):
    """Класс для работы с городами."""

    _city_repository: CityRepositoryInterface

    def __init__(self, city_repository: CityRepositoryInterface):
        self._city_repository = city_repository

    async def search_by_name(self, query: str) -> list[City]:
        """Конструктор для поиска по имени.

        :param _city_repository: CityRepositoryInterface
        :param query: str
        :returns: CityService
        """
        return await self._city_repository.search_by_name(query)

    async def search_by_coordinates(
        self,
        geo_integration: GeoServiceIntegrationInterface,
        latitude: str,
        longitude: str,
    ) -> 'CityService':
        """Поиск по координатам.

        :param geo_integration: GeoServiceIntegrationInterface
        :param latitude: str
        :param longitude: str
        :returns: CityService
        """
        coordinates_location_variants = await geo_integration.search(latitude, longitude)
        cities = await self._city_repository.search_by_variants(coordinates_location_variants)
        return CityService(cities, self._city_repository)


class CitySearchInterface(object):

    async def search(self):
        raise NotImplementedError


class SearchCityByName(CitySearchInterface):

    _city_service: CityService

    def __init__(self, city_service: CityService, query: str):
        self._city_service = city_service
        self._query = query

    async def search(self) -> list[City]:
        return await self._city_service.search_by_name(self._query)


class SearchCityByCoordinates(CitySearchInterface):

    _city_service: CityService
    _geo_service_integration: GeoServiceIntegrationInterface
    _latitude: str
    _longitude: str

    def __init__(
        self,
        city_service: CityService,
        geo_service_integration: GeoServiceIntegrationInterface,
        latitude: str,
        longitude: str,
    ):
        self._city_service = city_service
        self._geo_service_integration = geo_service_integration
        self._latitude = latitude
        self._longitude = longitude

    async def search(self) -> list[City]:
        city_name = await self._geo_service_integration.search(self._latitude, self._longitude)
        return await self._city_service.search_by_name(city_name)


class CitySearchInlineAnswer(object):

    _city_search: CitySearchInterface

    def __init__(self, city_search: CitySearchInterface):
        self._city_search = city_search

    async def to_inline_search_result(self) -> list[types.InlineQueryResult]:
        """Форматировать в ответ поиска.

        :returns: list[types.InlineQueryResultArticle]
        """
        cities = await self._city_search.search()
        return [
            types.InlineQueryResult(
                id=str(city.id),
                title=city.name,
                input_message_content=types.InputMessageContent(message_text='adf'),
            )
            for city in cities
        ]
