from aiogram import types

from db import db_connection
from integrations.client import IntegrationClient
from integrations.nominatim import NominatimIntegration
from repository.city import CityRepository
from services.city import Cities, CitiesCoordinatesSearch, CitiesCoordinatesSearchNotFoundSafety


async def location_handler(message: types.Message):
    """Обработчик, присланных боту геопозиций.

    :param message: types.Message
    """
    async with db_connection() as connection:
        answer = await CitiesCoordinatesSearchNotFoundSafety(
            CitiesCoordinatesSearch(
                Cities([], CityRepository(connection)),
                NominatimIntegration(
                    IntegrationClient(),
                ),
                message.location.latitude,
                message.location.longitude,
            ),
        ).to_answer()

    await answer.send(message.chat.id)
