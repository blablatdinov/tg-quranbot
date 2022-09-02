from aiogram import Bot, types
from loguru import logger

from exceptions.base_exception import InternalBotError
from exceptions.content_exceptions import NotFoundReferrerIdError, UserNotFoundError
from integrations.nats_integration import MessageBrokerInterface
from repository.users.registration import RegistrationRepositoryInterface
from repository.users.user import UserRepositoryInterface
from repository.users.users import UsersRepositoryInterface
from services.answers.answer import DefaultKeyboard, TextAnswer
from services.answers.answer_list import AnswersList
from services.answers.interface import AnswerInterface
from services.start_message import StartMessageInterface


class RegisterNewUser(AnswerInterface):
    """Регистрация нового пользователя."""

    def __init__(
        self,
        bot: Bot,
        chat_id: int,
        registration_repository: RegistrationRepositoryInterface,
    ):
        self._bot = bot
        self._chat_id = chat_id
        self._registration_repository = registration_repository

    async def send(self) -> list[types.Message]:
        """Конвертация в ответ.

        :return: AnswerInterface
        :raises InternalBotError: if user already exists
        """
        if await self._registration_repository.user_exists(self._chat_id):
            raise InternalBotError('User already exists')
        start_message = await self._registration_repository.admin_message()
        first_ayat = await self._registration_repository.first_ayat()
        await self._registration_repository.create(self._chat_id)
        return await AnswersList(
            TextAnswer(bot=self._bot, message=start_message, chat_id=self._chat_id, keyboard=DefaultKeyboard()),
            TextAnswer(
                bot=self._bot, message=str(first_ayat), chat_id=self._chat_id, keyboard=DefaultKeyboard(),
            ),
        ).send()


class RegisterUserWithReferrer(AnswerInterface):
    """Регистрация пользователя с реферером."""

    def __init__(  # noqa: WPS211 TODO: подумать как сократить
        self,
        bot: Bot,
        chat_id: int,
        register_new_user: AnswerInterface,
        user_repository: UserRepositoryInterface,
        start_message: StartMessageInterface,
    ):
        self._bot = bot
        self._chat_id = chat_id
        self._register_new_user = register_new_user
        self._user_repository = user_repository
        self._start_message = start_message

    async def send(self) -> list[types.Message]:
        """Создание пользователя.

        :return: AnswerInterface
        :raises NotFoundReferrerIdError: if referrer info is empty
        """
        referrer_id = await self._start_message.referrer_id()
        if not referrer_id:
            raise NotFoundReferrerIdError
        new_user_messages = await self._register_new_user.send()
        await self._user_repository.update_referrer(self._chat_id, referrer_id)
        referer_message = await TextAnswer(
            bot=self._bot,
            message='По вашей реферральной ссылке произошла регистрация',
            chat_id=referrer_id,
            keyboard=DefaultKeyboard(),
        ).send()
        return new_user_messages + referer_message


class RegisterAlreadyExistsUser(AnswerInterface):
    """Обработка регистрации, уже имеющегося пользователя."""

    _user_repository: UserRepositoryInterface
    _users_repository: UsersRepositoryInterface

    def __init__(
        self,
        bot: Bot,
        chat_id: int,
        user_repository: UserRepositoryInterface,
        users_repository: UsersRepositoryInterface,
    ):
        self._bot = bot
        self._chat_id = chat_id
        self._user_repository = user_repository
        self._users_repository = users_repository

    async def send(self) -> list[types.Message]:
        """Обработка уже зарегестрированного пользователя.

        :return: Answer
        """
        user = await self._user_repository.get_by_chat_id(self._chat_id)
        if user.is_active:
            return await TextAnswer(
                bot=self._bot,
                chat_id=self._chat_id,
                message='Вы уже зарегистрированы',
                keyboard=DefaultKeyboard(),
            ).send()

        await self._users_repository.update_status([self._chat_id], to=True)
        return await TextAnswer(
            bot=self._bot,
            chat_id=self._chat_id,
            message='Рады видеть вас снова, вы продолжите с дня {user_day}'.format(user_day=user.day),
            keyboard=DefaultKeyboard(),
        ).send()


class RegisterNewUserEvent(AnswerInterface):
    """Событие о регистрации нового пользователя."""

    def __init__(self, chat_id: int, answer: AnswerInterface, nats_integration: MessageBrokerInterface):
        self._chat_id = chat_id
        self._origin = answer
        self._message_broker = nats_integration

    async def send(self) -> list[types.Message]:
        """Отправка.

        :return: list[types.Message]
        """
        messages = await self._origin.send()
        await self._message_broker.send(
            {'user_id': self._chat_id},
            'User.Subscribed',
            1
        )
        return messages


class RegisterUser(AnswerInterface):
    """Класс осуществляющий регистрацию пользователя."""

    def __init__(
        self,
        register_new_user: AnswerInterface,
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
        logger.info('Registering user with chat_id: {0}'.format(self._chat_id))
        try:
            return await self._register_user_with_referrer.send()
        except NotFoundReferrerIdError:
            try:
                return await self._register_already_exists_user.send()
            except UserNotFoundError:
                return await self._register_new_user.send()
