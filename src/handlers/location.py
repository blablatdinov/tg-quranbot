from aiogram import types

from db import db_connection
from integrations.client import IntegrationClient
from integrations.nominatim import NominatimIntegration
from repository.city import CityRepository
from repository.user import UserRepository
from services.city.answers import CityNotSupportedSafetyAnswer, UserCity, UserCityAnswer
from services.city.search import SearchCityByCoordinates
from services.city.service import CityService


async def location_handler(message: types.Message):
    """Обработчик, присланных боту геопозиций.

    :param message: app_types.Message
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
                ),
            ),
        ).to_answer()

    await answer.send(message.chat.id)
