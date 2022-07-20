from aiogram import types

from db import DBConnection
from integrations.client import IntegrationClient
from integrations.nominatim import NominatimIntegration
from repository.city import CityRepository
from repository.update_log import UpdatesLogRepository
from repository.users.user import UserRepository
from services.answers.log_answer import LoggedAnswer, LoggedSourceMessageAnswerProcess
from services.city.answers import CityNotSupportedSafetyAnswer, UserCity, UserCityAnswer
from services.city.search import SearchCityByCoordinates
from services.city.service import CityService


async def location_handler(message: types.Message):
    """Обработчик, присланных боту геопозиций.

    :param message: app_types.Message
    """
    async with DBConnection() as connection:
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
        updates_log_repository = UpdatesLogRepository(connection)
        answer = LoggedSourceMessageAnswerProcess(
            updates_log_repository,
            message,
            LoggedAnswer(answer, updates_log_repository),
        )

    await answer.send(message.chat.id)
