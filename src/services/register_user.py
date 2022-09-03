import datetime

from aiogram import Bot, types
from databases.core import Database
from loguru import logger

from exceptions.base_exception import InternalBotError
from integrations.nats_integration import MessageBrokerInterface
from repository.users.registration import RegistrationRepositoryInterface
from repository.users.user import UserRepositoryInterface
from repository.users.users import UsersRepositoryInterface
from services.answers.answer import DefaultKeyboard, TextAnswer
from services.answers.answer_list import AnswersList
from services.answers.interface import AnswerInterface
from services.start_message import StartMessageInterface


class RegisterInterface(object):

    async def can(self, chat_id: int) -> bool:
        raise NotImplementedError

    async def register(self, chat_id: int) -> AnswerInterface:
        raise NotImplementedError


class RegisterNewUserEvent(RegisterInterface):

    def __init__(self, chat_id: int, origin: RegisterInterface, message_broker: MessageBrokerInterface):
        self._chat_id = chat_id
        self._origin = origin
        self._message_broker = message_broker

    async def can(self, chat_id: int) -> bool:
        return await self._origin.can(chat_id)

    async def register(self, chat_id: int) -> AnswerInterface:
        answer = await self._origin.register(chat_id)
        await self._message_broker.send(
            {
                'user_id': self._chat_id,
                'date_time': datetime.datetime.now().isoformat(),
                'referrer_id': None,
            },
            'User.Subscribed',
            1
        )
        return answer


class RegisterUserWithReferrerEvent(RegisterInterface):

    def __init__(
        self,
        chat_id: int,
        origin: RegisterInterface,
        message_broker: MessageBrokerInterface,
        start_message: StartMessageInterface
    ):
        self._chat_id = chat_id
        self._origin = origin
        self._message_broker = message_broker
        self._start_message = start_message

    async def can(self, chat_id: int) -> bool:
        return await self._origin.can(chat_id)

    async def register(self, chat_id: int) -> AnswerInterface:
        answer = await self._origin.register(chat_id)
        await self._message_broker.send(
            {
                'user_id': self._chat_id,
                'referrer_id': await self._start_message.referrer_id(),
                'date_time': datetime.datetime.now().isoformat(),
            },
            'User.Subscribed',
            1
        )
        return answer


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


class SafeRegistrationWithReferrer(RegisterInterface):

    def __init__(self, register_with_referrer: RegisterInterface, register_new_user: RegisterInterface, connection: Database):
        self._origin = register_with_referrer
        self._register_new_user = register_new_user
        self._connection = connection

    async def register(self, chat_id: int) -> AnswerInterface:
        txn = await self._connection.transaction()
        try:
            return await self._origin.register(chat_id)
        except Exception as error:
            logger.error('Error registration with referrer: {0}. Registration without referrer...'.format(str(error)))
            await txn.rollback()
        answer = await self._register_new_user.register(chat_id)
        return answer

    async def can(self, chat_id: int) -> bool:
        return await self._origin.can(chat_id)


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


class RegisterUser(AnswerInterface):
    """Класс осуществляющий регистрацию пользователя."""

    def __init__(
        self,
        register_new_user: RegisterInterface,
        register_user_with_referrer: RegisterInterface,
        register_already_exists_user: RegisterInterface,
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
            return await self._process_already_subscribed_user()
        if await self._register_user_with_referrer.can(self._chat_id):
            logger.info('Register chat_id: {0} with referrer'.format(self._chat_id))
            return await self._process_with_referrer()
        logger.info('Register new user chat_id: {0} without referrer'.format(self._chat_id))
        return await self._process_without_referrer()

    async def _process_already_subscribed_user(self):
        return await (await self._register_already_exists_user.register(self._chat_id)).send()

    async def _process_with_referrer(self):
        return await (await self._register_user_with_referrer.register(self._chat_id)).send()

    async def _process_without_referrer(self):
        return await (await self._register_new_user.register(self._chat_id)).send()
