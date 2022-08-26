from aiogram import types

from db.connection import database
from repository.city import CityRepository
from services.city.search import CitySearchInlineAnswer, SearchCityByName


async def inline_search_handler(query: types.InlineQuery):
    """Обработчик запросов поиска городов.

    :param query: app_types.InlineQuery
    """
    cities_query_answer = await CitySearchInlineAnswer(
        SearchCityByName(
            CityRepository(database),
            query.query,
        ),
    ).to_inline_search_result()

    await query.answer(cities_query_answer)
