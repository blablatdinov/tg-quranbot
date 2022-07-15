from aiogram import types

from db import DBConnection
from repository.city import CityRepository
from services.city.search import CitySearchInlineAnswer, SearchCityByName
from services.city.service import CityService


async def inline_search_handler(query: types.InlineQuery):
    """Обработчик запросов поиска городов.

    :param query: app_types.InlineQuery
    """
    async with DBConnection() as connection:
        cities_query_answer = await CitySearchInlineAnswer(
            SearchCityByName(
                CityService(
                    CityRepository(connection),
                ),
                query.query,
            ),
        ).to_inline_search_result()

    await query.answer(cities_query_answer)
