from dataclasses import dataclass

from aiogram import types

from answerable import Answerable
from exceptions import UserHasNotCityIdError
from integrations.nominatim import GeoServiceIntegrationInterface
from repository.city import City, CityRepositoryInterface
from services.answer import Answer, AnswerInterface


class Cities(object):
    """Класс для работы с городами."""

    _cities: list[City]
    _city_repository: CityRepositoryInterface

    def __init__(self, cities: list[City], city_repository: CityRepositoryInterface):
        self._cities = cities
        self._city_repository = city_repository

    @classmethod
    async def search(cls, _city_repository: CityRepositoryInterface, query: str) -> 'Cities':
        """Конструктор для поиска по имени.

        :param _city_repository: CityRepositoryInterface
        :param query: str
        :returns: Cities
        """
        # FIXME: logic in constructor
        cities = await _city_repository.search_by_name(query)
        return cls(cities, _city_repository)

    async def search_by_coordinates(
        self,
        geo_integration: GeoServiceIntegrationInterface,
        latitude: str,
        longitude: str,
    ) -> 'Cities':
        """Поиск по координатам.

        :param geo_integration: GeoServiceIntegrationInterface
        :param latitude: str
        :param longitude: str
        :returns: Cities
        """
        coordinates_location_variants = await geo_integration.search(latitude, longitude)
        cities = await self._city_repository.search_by_variants(coordinates_location_variants)
        return Cities(cities, self._city_repository)

    @property
    def exists(self) -> bool:
        """Проверяет длину найденных городов.

        :returns: bool
        """
        return bool(self._cities)

    def __str__(self):
        return str(self._cities)

    def __getitem__(self, get_item_input: int):
        return self._cities[get_item_input]

    def to_inline_search_result(self) -> list[types.InlineQueryResultArticle]:
        """Форматировать в ответ поиска.

        :returns: list[types.InlineQueryResultArticle]
        """
        return [
            types.InlineQueryResultArticle(
                id=str(city.id),
                title=city.name,
                input_message_content=types.InputMessageContent(message_text='adf'),
            )
            for city in self._cities
        ]


@dataclass
class CitiesCoordinatesSearch(object):
    """Класс для поиска по координатам."""

    cities: Cities
    geo_integration: GeoServiceIntegrationInterface
    latitude: str
    longitude: str

    async def to_answer(self) -> AnswerInterface:
        """Форматирование в ответ.

        :returns: AnswerInterface
        :raises UserHasNotCityIdError: если город не найден в БД
        """
        cities = await self.cities.search_by_coordinates(
            geo_integration=self.geo_integration,
            latitude=self.latitude,
            longitude=self.longitude,
        )
        if cities.exists == 0:
            raise UserHasNotCityIdError

        return Answer(message='Вам будет приходить время намаза для г. {0}'.format(cities[0].name))


@dataclass
class CitiesCoordinatesSearchNotFoundSafety(Answerable):
    """Декоратор, обрабатывающий исключение, в случае если пользователь без города запросил времена намазов."""

    origin: CitiesCoordinatesSearch

    async def to_answer(self) -> AnswerInterface:
        """Форматирование в ответ.

        :returns: AnswerInterface
        """
        try:
            return await self.origin.to_answer()
        except UserHasNotCityIdError as exception:
            return Answer(message=exception.message)
