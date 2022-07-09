from aiogram import types

from integrations.nominatim import NominatimIntegration
from repository.city import City, CityRepositoryInterface
from services.city import CitySearchInlineAnswer, CityService, SearchCityByCoordinates, SearchCityByName
from tests.mocks.integration_client import IntegrationClientMock


class CityRepositoryMock(CityRepositoryInterface):

    _storage: list[City] = [City(id=1, name='Казань')]

    async def search_by_name(self, query: str) -> list[City]:
        return list(
            filter(
                lambda city: city.name == query,
                self._storage
            )
        )


async def test():
    cities_query_answer = await CitySearchInlineAnswer(
        SearchCityByName(
            CityService(
                CityRepositoryMock(),
            ),
            'Казань'
        ),
    ).to_inline_search_result()

    assert isinstance(cities_query_answer, list)
    assert isinstance(cities_query_answer[0], types.InlineQueryResult)
    assert len(cities_query_answer) == 1


async def test_not_found():
    cities_query_answer = await CitySearchInlineAnswer(
        SearchCityByName(
            CityService(
                CityRepositoryMock(),
            ),
            'Неизвестный город'
        ),
    ).to_inline_search_result()

    assert isinstance(cities_query_answer, list)
    assert len(cities_query_answer) == 0


async def test_by_coordinates(path_to_nominatim_response_fixture):
    got = await SearchCityByCoordinates(
        CityService(
            CityRepositoryMock(),
        ),
        NominatimIntegration(
            IntegrationClientMock(path_to_nominatim_response_fixture),
        ),
        latitude='0',
        longitude='0',
    ).search()

    assert isinstance(got, list)
    assert got[0].name == 'Казань'
