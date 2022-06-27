from pydantic import BaseModel


class User(BaseModel):
    """Модель пользователя."""

    is_active: bool
    day: int


class UserRepositoryInterface(object):
    """Интерфейс репозитория для работы с пользователями."""

    async def create(self, chat_id: int):
        """Метод для создания пользователя.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def get(self, chat_id: int) -> User:
        """Метод для получения пользователя.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def exists(self, chat_id: int) -> bool:
        """Метод для проверки наличия пользователя в БД.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
