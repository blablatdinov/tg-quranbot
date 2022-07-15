from aiogram import types

from exceptions import CityNotSupportedError
from integrations.nominatim import GeoServiceIntegrationInterface
from repository.city import City
from services.city.service import CityService


class CitySearchInterface(object):
    """Интерфейс для поиска городов."""

    _city_service: CityService

    async def search(self) -> list[City]:
        """Осуществить поиск.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class SearchCityByName(CitySearchInterface):
    """Поиск города по названию."""

    _city_service: CityService

    def __init__(self, city_service: CityService, query: str):
        self._city_service = city_service
        self._query = query

    async def search(self) -> list[City]:
        """Осуществить поиск.

        :returns: list[City]
        """
        return await self._city_service.search_by_name(self._query)


class SearchCityByCoordinates(CitySearchInterface):
    """Поиск города по координатам."""

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
        """Осуществить поиск.

        :returns: list[City]
        :raises CityNotSupportedError: если город не найден в БД
        """
        city_name = await self._geo_service_integration.search(self._latitude, self._longitude)
        cities = await self._city_service.search_by_name(city_name)
        if not cities:
            template = 'Для города {0} я не знаю времен намазов, пожалуйста напишите моему разработчику'
            raise CityNotSupportedError(template.format(city_name))
        return cities


class CitySearchInlineAnswer(object):
    """Ответ на поиск."""

    _city_search: CitySearchInterface

    def __init__(self, city_search: CitySearchInterface):
        self._city_search = city_search

    async def to_inline_search_result(self) -> list[types.InlineQueryResultArticle]:
        """Форматировать в ответ поиска.

        :returns: list[app_types.InlineQueryResultArticle]
        """
        cities = await self._city_search.search()
        return [
            types.InlineQueryResultArticle(
                id=str(city.id),
                title=city.name,
                input_message_content=types.InputMessageContent(message_text=city.name),
            )
            for city in cities
        ]
