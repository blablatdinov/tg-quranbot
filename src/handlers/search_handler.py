from aiogram import types

from db import db_connection
from repository.city import CityRepository
from services.city import Cities


async def inline_search_handler(query: types.InlineQuery):
    async with db_connection() as connection:
        cities_query_answer = (
            await Cities.search(
                CityRepository(connection),
                query.query,
            )
        ).to_inline_search_result()

    await query.answer(cities_query_answer)
