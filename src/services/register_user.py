from aiogram import Bot, types

from exceptions.base_exception import InternalBotError
from repository.admin_message import AdminMessageRepositoryInterface
from repository.ayats.ayat import AyatRepositoryInterface
from repository.users.user import User, UserRepositoryInterface
from repository.users.users import UsersRepositoryInterface
from services.answers.answer import TextAnswer, DefaultKeyboard
from services.answers.answer_list import AnswersList
from services.answers.interface import AnswerInterface
from services.start_message import StartMessageMeta


class RegisterNewUser(object):
    """Регистрация нового пользователя."""

    _user_repository: UserRepositoryInterface
    _admin_messages_repository: AdminMessageRepositoryInterface
    _ayats_repository: AyatRepositoryInterface

    def __init__(
        self,
        bot: Bot,
        chat_id: int,
        user_repository: UserRepositoryInterface,
        admin_messages_repository: AdminMessageRepositoryInterface,
        ayats_repository: AyatRepositoryInterface,
    ):
        self._bot = bot
        self._chat_id = chat_id
        self._user_repository = user_repository
        self._admin_messages_repository = admin_messages_repository
        self._ayats_repository = ayats_repository

    async def can(self, chat_id) -> bool:
        """Проверка возможности регистрации.

        :param chat_id: int
        :returns: bool
        """
        return not await self._user_repository.exists(chat_id)

    async def send(self) -> list[types.Message]:
        """Конвертация в ответ.

        :return: AnswerInterface
        """
        start_message = await self._admin_messages_repository.get('start')
        first_ayat = await self._ayats_repository.get(1)
        await self._user_repository.create(self._chat_id)
        return await AnswersList(
            TextAnswer(bot=self._bot, message=start_message, chat_id=self._chat_id, keyboard=DefaultKeyboard()),
            TextAnswer(bot=self._bot, message=str(first_ayat), chat_id=self._chat_id, keyboard=DefaultKeyboard()),
        ).send()


class RegisterUserWithReferrer(AnswerInterface):
    """Регистрация пользователя с реферером."""

    _register_new_user: RegisterNewUser
    _user_repository: UserRepositoryInterface
    _start_message_meta: StartMessageMeta

    def __init__(
        self,
        bot: Bot,
        chat_id: int,
        register_new_user: RegisterNewUser,
        user_repository: UserRepositoryInterface,
        start_message_meta: StartMessageMeta,
    ):
        self._bot = bot
        self._chat_id = chat_id
        self._register_new_user = register_new_user
        self._user_repository = user_repository
        self._start_message_meta = start_message_meta

    def can(self) -> bool:
        """Проверка возможности зарегестрировать пользователя с реферрером.

        :return: bool
        """
        return bool(self._start_message_meta.referrer)

    async def send(self) -> list[types.Message]:
        """Создание пользователя.

        :return: AnswerInterface
        :raises InternalBotError: if referrer info is empty
        """
        if not self._start_message_meta.referrer:
            raise InternalBotError
        new_user_messages = await self._register_new_user.send()
        referer_chat_id = await self._get_referer_chat_id()
        await self._user_repository.update_referrer(self._chat_id, referer_chat_id)
        referer_message = await TextAnswer(
            bot=self._bot,
            message='По вашей реферральной ссылке произошла регистрация',
            chat_id=referer_chat_id,
            keyboard=DefaultKeyboard()
        ).send()
        return new_user_messages + referer_message

    async def _get_referer_chat_id(self) -> int:
        max_legacy_referrer_id = 3000
        if self._start_message_meta.referrer <= max_legacy_referrer_id:
            referrer_user_record = await self._user_repository.get_by_id(self._start_message_meta.referrer)
        else:
            referrer_user_record = (await self._user_repository.get_by_id(self._start_message_meta.referrer)).chat_id

        return referrer_user_record.chat_id


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
                keyboard=DefaultKeyboard()
            ).send()

        await self._users_repository.update_status([self._chat_id], to=True)
        return await TextAnswer(
            bot=self._bot,
            chat_id=self._chat_id,
            message='Рады видеть вас снова, вы продолжите с дня {user_day}'.format(user_day=user.day),
            keyboard=DefaultKeyboard(),
        ).send()


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
        if not await self._register_new_user.can(self._chat_id):
            return await self._register_already_exists_user.send()

        if self._register_user_with_referrer.can():
            return await self._register_user_with_referrer.send()

        return await self._register_new_user.send()
