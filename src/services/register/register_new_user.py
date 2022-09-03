from aiogram import Bot
from loguru import logger

from repository.users.registration import RegistrationRepositoryInterface
from services.answers.answer import DefaultKeyboard, TextAnswer
from services.answers.answer_list import AnswersList
from services.answers.interface import AnswerInterface
from services.register.register_interface import RegisterInterface


class RegisterNewUser(RegisterInterface):
    """Регистрация нового пользователя."""

    def __init__(
        self,
        bot: Bot,
        registration_repository: RegistrationRepositoryInterface,
    ):
        self._bot = bot
        self._registration_repository = registration_repository

    async def can(self, chat_id: int) -> bool:
        """Проверка возможности регистрации.

        :param chat_id: int
        :returns: bool
        """
        return not await self._registration_repository.user_exists(chat_id)

    async def register(self, chat_id: int) -> AnswerInterface:
        """Создание пользователя.

        :param chat_id: int
        :returns: User
        """
        logger.info('Registration new User <{0}> without referrer...'.format(chat_id))
        await self._registration_repository.create(chat_id)
        start_message = await self._registration_repository.admin_message()
        first_ayat = await self._registration_repository.first_ayat()
        logger.info('User <{0}> registered without referrer'.format(chat_id))
        return AnswersList(
            TextAnswer(self._bot, chat_id, start_message, DefaultKeyboard()),
            TextAnswer(self._bot, chat_id, str(first_ayat), DefaultKeyboard()),
        )
