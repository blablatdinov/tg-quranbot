from aiogram import Bot, types
from loguru import logger

from exceptions.base_exception import InternalBotError
from repository.users.registration import RegistrationRepositoryInterface
from repository.users.user import UserRepositoryInterface
from repository.users.users import UsersRepositoryInterface
from services.answers.answer import TextAnswer, DefaultKeyboard
from services.answers.answer_list import AnswersList
from services.answers.interface import AnswerInterface
from services.start_message import StartMessageInterface


class RegisterNewUser(object):
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
        await self._registration_repository.create(chat_id)
        start_message = await self._registration_repository.admin_message()
        first_ayat = await self._registration_repository.first_ayat()
        return AnswersList(
            TextAnswer(self._bot, chat_id, start_message, DefaultKeyboard()),
            TextAnswer(self._bot, chat_id, str(first_ayat), DefaultKeyboard()),
        )


class RegisterUserWithReferrer(object):
    """Регистрация пользователя с реферером."""

    def __init__(
        self,
        bot: Bot,
        register_new_user: RegisterNewUser,
        user_repository: UserRepositoryInterface,
        start_message: StartMessageInterface,
    ):
        self._bot = bot
        self._register_new_user = register_new_user
        self._user_repository = user_repository
        self._start_message = start_message

    async def can(self) -> bool:
        """Проверка возможности зарегистрировать пользователя с реферером.

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


class RegisterAlreadyExistsUser(object):
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


class RegisterUser(AnswerInterface):
    """Класс осуществляющий регистрацию пользователя."""

    _register_new_user: RegisterNewUser
    _register_user_with_referrer: RegisterUserWithReferrer
    _register_already_exists_user: RegisterAlreadyExistsUser
    _chat_id: int

    def __init__(
        self,
        register_new_user: RegisterNewUser,
        register_user_with_referrer: RegisterUserWithReferrer,
        register_already_exists_user: RegisterAlreadyExistsUser,
        chat_id: int,
    ):
        self._register_new_user = register_new_user
        self._register_user_with_referrer = register_user_with_referrer
        self._register_already_exists_user = register_already_exists_user
        self._chat_id = chat_id

    async def send(self) -> list[types.Message]:
        """Entrypoint.

        :returns: str Ответ пользователю
        """
        logger.info('Process start message for chat_id: {0}'.format(self._chat_id))
        if not await self._register_new_user.can(self._chat_id):
            logger.info('User <{0}> already subscribed'.format(self._chat_id))
            return await (await self._register_already_exists_user.register(self._chat_id)).send()

        if await self._register_user_with_referrer.can():
            logger.info('Register chat_id: {0} with referrer'.format(self._chat_id))
            return await (await self._register_user_with_referrer.register(self._chat_id)).send()

        logger.info('Register new user chat_id: {0} without referrer'.format(self._chat_id))
        return await (await self._register_new_user.register(self._chat_id)).send()
