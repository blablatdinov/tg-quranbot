from aiogram import types
from aiogram.dispatcher import FSMContext

from db.connection import database
from integrations.client import IntegrationClient, LoggedIntegrationClient
from integrations.nominatim import NominatimIntegration
from repository.city import CityRepository
from repository.users.user import UserRepository
from services.city.answers import CityNotSupportedSafetyAnswer, UserCity, UserCityAnswer
from services.city.search import SearchCityByCoordinates
from utlls import BotInstance


async def location_handler(message: types.Message, state: FSMContext):
    """Обработчик, присланных боту геопозиций.

    :param message: types.Message
    :param state: FSMContext
    """
    await CityNotSupportedSafetyAnswer(
        BotInstance.get(),
        message.chat.id,
        UserCityAnswer(
            BotInstance.get(),
            message.chat.id,
            UserCity(
                SearchCityByCoordinates(
                    CityRepository(database),
                    NominatimIntegration(
                        LoggedIntegrationClient(
                            IntegrationClient(),
                        ),
                    ),
                    latitude=message.location.latitude,
                    longitude=message.location.longitude,
                ),
                UserRepository(database),
                message.chat.id,
            ),
        ),
    ).send()

    await state.finish()
