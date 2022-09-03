from aiogram import Bot

from exceptions.base_exception import InternalBotError
from repository.users.user import UserRepositoryInterface
from services.answers.answer import DefaultKeyboard, TextAnswer
from services.answers.answer_list import AnswersList
from services.answers.interface import AnswerInterface
from services.register.register_interface import RegisterInterface
from services.start_message import StartMessageInterface


class RegisterUserWithReferrer(RegisterInterface):
    """Регистрация пользователя с реферером."""

    def __init__(
        self,
        bot: Bot,
        register_new_user: RegisterInterface,
        user_repository: UserRepositoryInterface,
        start_message: StartMessageInterface,
    ):
        self._bot = bot
        self._register_new_user = register_new_user
        self._user_repository = user_repository
        self._start_message = start_message

    async def can(self, chat_id: int) -> bool:
        """Проверка возможности зарегистрировать пользователя с реферером.

        :param chat_id: int
        :return: bool
        """
        return bool(await self._start_message.referrer_id())

    async def register(self, chat_id: int) -> AnswerInterface:
        """Создание пользователя.

        :param chat_id: int
        :return: AnswerInterface
        :raises InternalBotError: if referrer info is empty
        """
        new_user_answers = await self._register_new_user.register(chat_id)
        if not await self._start_message.referrer_id():
            raise InternalBotError
        await self._user_repository.update_referrer(chat_id, await self._start_message.referrer_id())
        message_for_referrer = 'По вашей реферальной ссылке произошла регистрация'
        return AnswersList(
            new_user_answers,
            TextAnswer(
                self._bot,
                await self._start_message.referrer_id(),
                message_for_referrer,
                DefaultKeyboard(),
            ),
        )
