from typing import Optional

from repository.admin_message import AdminMessageRepositoryInterface
from repository.ayats.ayat import AyatRepositoryInterface
from repository.users.user import UserRepositoryInterface


class RegistrationRepositoryInterface(object):
    """Интерфейс для регистрации пользователя."""

    async def user_exists(self, chat_id: int):
        """Проверить наличие пользователя.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def admin_message(self):
        """Получить административное сообщение.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def first_ayat(self):
        """Получить первый аят.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def create(self, chat_id: int, referrer_id: Optional[int] = None):
        """Создать пользователя.

        :param chat_id: int
        :param referrer_id: Optional[int]
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class RegistrationRepository(RegistrationRepositoryInterface):
    """Класс работы с хранилищем для регистрации пользователя."""

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        admin_messages_repository: AdminMessageRepositoryInterface,
        ayats_repository: AyatRepositoryInterface,
    ):
        self._user_repository = user_repository
        self._admin_messages_repository = admin_messages_repository
        self._ayats_repository = ayats_repository

    async def user_exists(self, chat_id: int):
        """Проверить наличие пользователя.

        :param chat_id: int
        :return: bool
        """
        return await self._user_repository.exists(chat_id)

    async def admin_message(self):
        """Получить административное сообщение.

        :return: str
        """
        return await self._admin_messages_repository.get('start')

    async def first_ayat(self):
        """Получить первый аят.

        :return: Ayat
        """
        return await self._ayats_repository.get(1)

    async def create(self, chat_id: int, referrer_id: Optional[int] = None):
        """Создать пользователя.

        :param chat_id: int
        :param referrer_id: Optional[int]
        """
        await self._user_repository.create(chat_id, referrer_id)
