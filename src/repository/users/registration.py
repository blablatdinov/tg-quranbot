from typing import Optional, Protocol

from repository.admin_message import AdminMessageInterface
from repository.ayats.ayat import AyatRepositoryInterface
from repository.ayats.schemas import Ayat
from repository.users.user import UserRepositoryInterface


class RegistrationRepositoryInterface(Protocol):
    """Интерфейс для регистрации пользователя."""

    async def user_exists(self, chat_id: int):
        """Проверить наличие пользователя.

        :param chat_id: int
        """

    async def admin_message(self) -> str:
        """Получить административное сообщение."""

    async def first_ayat(self) -> Ayat:
        """Получить первый аят."""

    async def create(self, chat_id: int, referrer_id: Optional[int] = None):
        """Создать пользователя.

        :param chat_id: int
        :param referrer_id: Optional[int]
        """


class RegistrationRepository(RegistrationRepositoryInterface):
    """Класс работы с хранилищем для регистрации пользователя."""

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        admin_message: AdminMessageInterface,
        ayats_repository: AyatRepositoryInterface,
    ):
        """Конструктор класса.

        :param user_repository: UserRepositoryInterface
        :param admin_message: AdminMessageInterface
        :param ayats_repository: AyatRepositoryInterface
        """
        self._user_repository = user_repository
        self._admin_message = admin_message
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
        return await self._admin_message.text()

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
