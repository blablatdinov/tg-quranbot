from dataclasses import field, dataclass

from aiogram import types

from exceptions import UserHasNotCityId
from integrations.nominatim import GeoServiceIntegrationInterface
from repository.city import CityRepositoryInterface, City
from services.answer import Answer


class Cities(object):

    _cities: list[City]
    _city_repository: CityRepositoryInterface

    def __init__(self, cities: list[City], city_repository: CityRepositoryInterface):
        self._cities = cities
        self._city_repository = city_repository

    @classmethod
    async def search(cls, _city_repository: CityRepositoryInterface, query: str) -> 'Cities':
        cities = await _city_repository.search_by_name(query)
        return cls(cities, _city_repository)

    async def search_by_coordinates(
        self,
        geo_integration: GeoServiceIntegrationInterface,
        latitude: str,
        longitude: str,
    ) -> 'Cities':
        coordinates_location_variants = await geo_integration.search(latitude, longitude)
        cities = await self._city_repository.search_by_variants(coordinates_location_variants)
        return Cities(cities, self._city_repository)

    def __str__(self):
        return str(self._cities)

    def __len__(self):
        return len(self._cities)

    def __getitem__(self, item: int):
        return self._cities[item]

    def to_inline_search_result(self) -> list[types.InlineQueryResultArticle]:
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
    cities: Cities
    geo_integration: GeoServiceIntegrationInterface
    latitude: str
    longitude: str

    async def to_answer(self):
        cities = await self.cities.search_by_coordinates(
            geo_integration=self.geo_integration,
            latitude=self.latitude,
            longitude=self.longitude,
        )
        if len(cities) == 0:
            raise UserHasNotCityId

        return Answer(message='Вам будет приходить время намаза для г. {0}'.format(cities[0].name))


@dataclass
class CitiesCoordinatesSearchNotFoundSafety(object):
    origin: CitiesCoordinatesSearch

    async def to_answer(self):
        try:
            return await self.origin.to_answer()
        except UserHasNotCityId as e:
            return Answer(message=e.message)
