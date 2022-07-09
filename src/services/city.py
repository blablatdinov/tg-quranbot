from aiogram import types

from answerable import Answerable
from exceptions import CityNotSupportedError
from integrations.nominatim import GeoServiceIntegrationInterface
from repository.city import City, CityRepositoryInterface
from repository.user import UserRepositoryInterface
from services.answer import Answer, AnswerInterface


class CityService(object):
    """Класс для работы с городами."""

    _city_repository: CityRepositoryInterface

    def __init__(self, city_repository: CityRepositoryInterface):
        self._city_repository = city_repository

    async def search_by_name(self, query: str) -> list[City]:
        """Конструктор для поиска по имени.

        :param query: str
        :returns: CityService
        """
        return await self._city_repository.search_by_name(query)


class CitySearchInterface(object):

    _city_service: CityService

    async def search(self) -> list[City]:
        raise NotImplementedError


class SearchCityByName(CitySearchInterface):

    _city_service: CityService

    def __init__(self, city_service: CityService, query: str):
        self._city_service = city_service
        self._query = query

    async def search(self) -> list[City]:
        return await self._city_service.search_by_name(self._query)


class UserCity(object):

    _city_search: CitySearchInterface
    _user_repository: UserRepositoryInterface
    _chat_id: int

    def __init__(self, city_search: CitySearchInterface, user_repository: UserRepositoryInterface, chat_id: int):
        self._city_search = city_search
        self._user_repository = user_repository
        self._chat_id = chat_id

    async def update_city(self) -> City:
        city = (await self._city_search.search())[0]
        await self._user_repository.update_city(self._chat_id, city.id)
        return city


class UserCityAnswer(Answerable):

    _user_city: UserCity

    def __init__(self, user_city: UserCity):
        self._user_city = user_city

    async def to_answer(self) -> AnswerInterface:
        city = await self._user_city.update_city()
        return Answer(message='Вам будет приходить время намаза для г. {}'.format(city.name))


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
        cities = await self._city_service.search_by_name(city_name)
        if len(cities) == 0:
            template = 'Для города {0} я не знаю времен намазов, пожалуйста напишите моему разработчику'
            raise CityNotSupportedError(template.format(city_name))
        return cities


class CityNotSupportedSafetyAnswer(Answerable):

    def __init__(self, answer: Answerable):
        self._origin = answer

    async def to_answer(self) -> AnswerInterface:
        try:
            return await self._origin.to_answer()
        except CityNotSupportedError as error:
            return Answer(message=error.message)


class CitySearchInlineAnswer(object):

    _city_search: CitySearchInterface

    def __init__(self, city_search: CitySearchInterface):
        self._city_search = city_search

    async def to_inline_search_result(self) -> list[types.InlineQueryResultArticle]:
        """Форматировать в ответ поиска.

        :returns: list[types.InlineQueryResultArticle]
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
