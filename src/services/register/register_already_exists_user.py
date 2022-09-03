from aiogram import Bot

from repository.users.user import UserRepositoryInterface
from repository.users.users import UsersRepositoryInterface
from services.answers.answer import DefaultKeyboard, TextAnswer
from services.answers.interface import AnswerInterface
from services.register.register_interface import RegisterInterface


class RegisterAlreadyExistsUser(RegisterInterface):
    """Обработка регистрации, уже имеющегося пользователя."""

    def __init__(
        self,
        bot: Bot,
        user_repository: UserRepositoryInterface,
        users_repository: UsersRepositoryInterface,
    ):
        self._bot = bot
        self._user_repository = user_repository
        self._users_repository = users_repository

    async def can(self, chat_id: int) -> bool:
        """Проверка возможности регистрации.

        :param chat_id: int
        :return: bool
        """
        return True

    async def register(self, chat_id: int) -> AnswerInterface:
        """Обработка уже зарегестрированного пользователя.

        :param chat_id: int
        :return: Answer
        """
        user = await self._user_repository.get_by_chat_id(chat_id)
        if user.is_active:
            return TextAnswer(self._bot, chat_id, 'Вы уже зарегистрированы', DefaultKeyboard())

        await self._users_repository.update_status([chat_id], to=True)
        return TextAnswer(
            self._bot,
            chat_id,
            'Рады видеть вас снова, вы продолжите с дня {user_day}'.format(user_day=user.day),
            DefaultKeyboard(),
        )
