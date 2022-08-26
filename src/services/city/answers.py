from aiogram import types, Bot
from loguru import logger

from exceptions.content_exceptions import CityNotSupportedError
from repository.city import City
from repository.users.user import UserRepositoryInterface
from services.answers.answer import TextAnswer, DefaultKeyboard
from services.answers.interface import AnswerInterface
from services.city.search import CitySearchInterface


class UserCity(object):
    """Класс обслуживающий город пользователя."""

    _city_search: CitySearchInterface
    _user_repository: UserRepositoryInterface
    _chat_id: int

    def __init__(self, city_search: CitySearchInterface, user_repository: UserRepositoryInterface, chat_id: int):
        self._city_search = city_search
        self._user_repository = user_repository
        self._chat_id = chat_id

    async def update_city(self) -> City:
        """Обновить город.

        :returns: City
        """
        city = (await self._city_search.search())[0]
        logger.info('Try update user <{0}> city to {1}'.format(self._chat_id, city))
        await self._user_repository.update_city(self._chat_id, city.id)
        logger.info('User <{0}> city updated to {1}'.format(self._chat_id, city))
        return city


class UserCityAnswer(AnswerInterface):
    """Ответ пользователю о смене города."""

    _user_city: UserCity

    def __init__(self, bot: Bot, chat_id: int, user_city: UserCity):
        self._bot = bot
        self._chat_id = chat_id
        self._user_city = user_city

    async def send(self) -> list[types.Message]:
        """Форматировать в ответ.

        :returns: AnswerInterface
        """
        city = await self._user_city.update_city()
        return await TextAnswer(
            self._bot,
            self._chat_id,
            'Вам будет приходить время намаза для г. {0}'.format(city.name),
            DefaultKeyboard(),
        ).send()


class CityNotSupportedSafetyAnswer(AnswerInterface):
    """Ответ на поиск с обраоткой ошибки о необслуживаемом городе."""

    def __init__(self, bot: Bot, chat_id: int, answer: AnswerInterface):
        self._bot = bot
        self._chat_id = chat_id
        self._origin = answer

    async def send(self) -> list[types.Message]:
        """Форматировать в ответ.

        :returns: AnswerInterface
        """
        try:
            return await self._origin.send()
        except CityNotSupportedError as error:
            return await TextAnswer(
                self._bot,
                self._chat_id,
                error.user_message,
                DefaultKeyboard(),
            ).send()
