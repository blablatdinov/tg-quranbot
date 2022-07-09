from dataclasses import dataclass, field

from aiogram import types

from repository.city import CityRepositoryInterface, City


class Cities(object):

    _city_repository: CityRepositoryInterface
    _cities: list[City] = field(default_factory=list)

    def __init__(self, city_repository: CityRepositoryInterface, cities: list[City]):
        self._city_repository = city_repository
        self._cities = cities

    @classmethod
    async def search(cls, _city_repository: CityRepositoryInterface, query: str) -> 'Cities':
        cities = await _city_repository.search_by_name(query)
        return cls(_city_repository, cities)

    def __str__(self):
        return str(self._cities)

    def to_inline_search_result(self) -> list[types.InlineQueryResultArticle]:
        return [
            types.InlineQueryResultArticle(
                id=str(city.id),
                title=city.name,
                input_message_content=types.InputMessageContent(message_text='adf'),
            )
            for city in self._cities
        ]
