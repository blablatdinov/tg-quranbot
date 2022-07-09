from aiogram import types

from db import db_connection
from integrations.client import IntegrationClient
from integrations.nominatim import NominatimIntegration
from repository.city import CityRepository
from repository.user import UserRepository
from services.city import CityService, SearchCityByCoordinates, UserCity, UserCityAnswer, CityNotSupportedSafetyAnswer


async def location_handler(message: types.Message):
    """Обработчик, присланных боту геопозиций.

    :param message: types.Message
    """
    async with db_connection() as connection:
        answer = await CityNotSupportedSafetyAnswer(
            UserCityAnswer(
                UserCity(
                    SearchCityByCoordinates(
                        CityService(
                            CityRepository(connection),
                        ),
                        NominatimIntegration(
                            IntegrationClient(),
                        ),
                        latitude=message.location.latitude,
                        longitude=message.location.longitude,
                    ),
                    UserRepository(connection),
                    message.chat.id,
                )
            )
        ).to_answer()

    await answer.send(message.chat.id)
