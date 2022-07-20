from exceptions import InternalBotError
from repository.admin_message import AdminMessageRepositoryInterface
from repository.ayats.ayat import AyatRepositoryInterface
from repository.users.user import User, UserRepositoryInterface
from repository.users.user_actions import UserActionEnum, UserActionRepositoryInterface
from repository.users.users import UsersRepositoryInterface
from services.answers.answer import Answer
from services.answers.answer_list import AnswersList
from services.answers.interface import AnswerInterface
from services.start_message import StartMessageMeta


class RegisterNewUser(object):
    """Регистрация нового пользователя."""

    _user_repository: UserRepositoryInterface
    _user_action_repository: UserActionRepositoryInterface
    _admin_messages_repository: AdminMessageRepositoryInterface
    _ayats_repository: AyatRepositoryInterface

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        user_action_repository: UserActionRepositoryInterface,
        admin_messages_repository: AdminMessageRepositoryInterface,
        ayats_repository: AyatRepositoryInterface,
    ):
        self._user_repository = user_repository
        self._user_action_repository = user_action_repository
        self._admin_messages_repository = admin_messages_repository
        self._ayats_repository = ayats_repository

    async def can(self, chat_id) -> bool:
        """Проверка возможности регистрации.

        :param chat_id: int
        :returns: bool
        """
        return not await self._user_repository.exists(chat_id)

    async def register(self, chat_id: int) -> User:
        """Создание пользователя.

        :param chat_id: int
        :returns: User
        """
        user = await self._user_repository.create(chat_id)
        await self._user_action_repository.create_user_action(chat_id, UserActionEnum.SUBSCRIBED)
        return user

    async def to_answer(self, chat_id: int) -> AnswerInterface:
        """Конвертация в ответ.

        :param chat_id: int
        :return: AnswerInterface
        """
        start_message = await self._admin_messages_repository.get('start')
        first_ayat = await self._ayats_repository.get(1)
        return AnswersList(
            Answer(message=start_message, chat_id=chat_id),
            Answer(message=str(first_ayat), chat_id=chat_id),
        )


class RegisterUserWithReferrer(object):
    """Регистрация пользователя с реферером."""

    _register_new_user: RegisterNewUser
    _user_repository: UserRepositoryInterface
    _start_message_meta: StartMessageMeta

    def __init__(
        self,
        register_new_user: RegisterNewUser,
        user_repository: UserRepositoryInterface,
        start_message_meta: StartMessageMeta,
    ):
        self._register_new_user = register_new_user
        self._user_repository = user_repository
        self._start_message_meta = start_message_meta

    def can(self) -> bool:
        """Проверка возможности зарегестрировать пользователя с реферрером.

        :return: bool
        """
        return bool(self._start_message_meta.referrer)

    async def register(self, chat_id: int) -> AnswerInterface:
        """Создание пользователя.

        :param chat_id: int
        :return: AnswerInterface
        :raises InternalBotError: if referrer info is empty
        """
        await self._register_new_user.register(chat_id)
        if not self._start_message_meta.referrer:
            raise InternalBotError
        await self._user_repository.update_referrer(chat_id, self._start_message_meta.referrer)
        message_for_referrer = 'По вашей реферральной ссылке произошла регистрация'
        referrer_user_record = await self._user_repository.get_by_id(self._start_message_meta.referrer)
        new_user_answers = await self._register_new_user.to_answer(chat_id)
        new_user_answers_list = new_user_answers.to_list()
        return AnswersList(
            new_user_answers_list[0],
            new_user_answers_list[1],
            Answer(message=message_for_referrer, chat_id=referrer_user_record.chat_id),
        )


class RegisterAlreadyExistsUser(object):
    """Обработка регистрации, уже имеющегося пользователя."""

    _user_repository: UserRepositoryInterface
    _users_repository: UsersRepositoryInterface
    _user_action_repository: UserActionRepositoryInterface

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        user_action_repository: UserActionRepositoryInterface,
        users_repository: UsersRepositoryInterface,
    ):
        self._user_repository = user_repository
        self._users_repository = users_repository
        self._user_action_repository = user_action_repository

    async def register(self, chat_id: int) -> Answer:
        """Обработка уже зарегестрированного пользователя.

        :param chat_id: int
        :return: Answer
        """
        user = await self._user_repository.get_by_chat_id(chat_id)
        if user.is_active:
            return Answer(chat_id=chat_id, message='Вы уже зарегистрированы')

        await self._user_action_repository.create_user_action(chat_id, UserActionEnum.REACTIVATED)
        await self._users_repository.update_status([chat_id], to=True)
        return Answer(
            chat_id=chat_id,
            message='Рады видеть вас снова, вы продолжите с дня {user_day}'.format(user_day=user.day),
        )


class RegisterUser(object):
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

    async def register(self) -> AnswerInterface:
        """Entrypoint.

        :returns: str Ответ пользователю
        """
        if not await self._register_new_user.can(self._chat_id):
            return await self._register_already_exists_user.register(self._chat_id)

        if self._register_user_with_referrer.can():
            return await self._register_user_with_referrer.register(self._chat_id)

        await self._register_new_user.register(self._chat_id)
        return await self._register_new_user.to_answer(self._chat_id)
