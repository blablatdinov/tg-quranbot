from pydantic import BaseModel


class User(BaseModel):
    is_active: bool


class UserRepositoryInterface(object):
    """Интерфейс репозитория для работы с пользователями."""

    async def create(self, chat_id: int):
        """Метод для создания пользователя.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def get(self, chat_id: int) -> User:
        raise NotImplementedError

    async def exists(self, chat_id: int):
        raise NotImplementedError

    async def status(self, chat_id: int):
        raise NotImplementedError
