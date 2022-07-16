from typing import Optional

from repository.admin_message import AdminMessageRepositoryInterface
from repository.users.user import User, UserRepositoryInterface
from repository.users.user_actions import UserActionEnum, UserActionRepositoryInterface


class UserRegistrationRepositoryInterface(object):
    """Интерфейс для классов объеденящий методы для регистрации пользователя."""

    async def check_user_exists(self, chat_id: int):
        """Метод для проверки наличия пользователя в БД.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def create_user(self, chat_id: int, referrer_id: Optional[int]):
        """Метод для создания пользователя.

        :param chat_id: int
        :param referrer_id: Optional[int]
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def create_user_action(self, chat_id: int, action: UserActionEnum):
        """Создать действие пользователя.

        :param chat_id: int
        :param action: UserActionEnum
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def get_user_by_chat_id(self, chat_id: int) -> User:
        """Метод для получения пользователя.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def get_by_id(self, user_id: int) -> User:
        """Метод для получения пользователя.

        :param user_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def get_admin_message(self, key: str) -> str:
        """Получить административное сообщение по ключу.

        :param key: str
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class UserRegistrationRepository(UserRegistrationRepositoryInterface):
    """Класс, объеденящий методы для регистрации пользователя."""

    _user_repository: UserRepositoryInterface
    _user_action_repository: UserActionRepositoryInterface
    _admin_messages_repository: AdminMessageRepositoryInterface

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        user_action_repository: UserActionRepositoryInterface,
        admin_messages_repository: AdminMessageRepositoryInterface,
    ):
        self._user_repository = user_repository
        self._user_action_repository = user_action_repository
        self._admin_messages_repository = admin_messages_repository

    async def check_user_exists(self, chat_id: int):
        """Метод для проверки наличия пользователя в БД.

        :param chat_id: int
        :returns: bool
        """
        return await self._user_repository.exists(chat_id)

    async def create_user(self, chat_id: int, referrer_id: Optional[int]):
        """Метод для создания пользователя.

        :param chat_id: int
        :param referrer_id: Optional[int]
        """
        await self._user_repository.create(chat_id, referrer_id)

    async def create_user_action(self, chat_id: int, action: UserActionEnum):
        """Создать действие пользователя.

        :param chat_id: int
        :param action: UserActionEnum
        """
        await self._user_action_repository.create_user_action(chat_id, action)

    async def get_user_by_chat_id(self, chat_id: int) -> User:
        """Метод для получения пользователя.

        :param chat_id: int
        :returns: User
        """
        return await self._user_repository.get_by_chat_id(chat_id)

    async def get_by_id(self, user_id: int) -> User:
        """Метод для получения пользователя.

        :param user_id: int
        :returns: User
        """
        return await self._user_repository.get_by_id(user_id)

    async def get_admin_message(self, key: str) -> str:
        """Получить административное сообщение по ключу.

        :param key: str
        :returns: str
        """
        return await self._admin_messages_repository.get(key)
