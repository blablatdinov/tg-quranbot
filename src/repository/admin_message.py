from typing import Protocol

from databases import Database
from pydantic import BaseModel

from exceptions.base_exception import InternalBotError


class QueryResult(BaseModel):
    """Резултат запроса на получение административного сообщения."""

    text: str


class AdminMessageRepositoryInterface(Protocol):
    """Интерфейс репозитория для работы с административными сообщениями."""

    async def get(self, key: str) -> str:
        """Метод для получения административного сообщения.

        :param key: str
        """


class AdminMessageRepository(AdminMessageRepositoryInterface):
    """Класс для работы с БД."""

    def __init__(self, connection: Database):
        self.connection = connection

    async def get(self, key: str) -> str:
        """Получить административное сообщение по ключу.

        :param key: str
        :returns: str
        :raises InternalBotError: возбуждается если административное сообщение с переданным ключом не найдено
        """
        record = await self.connection.fetch_one(
            'SELECT text FROM admin_messages m WHERE m.key = :key', {'key': key},
        )
        if not record:
            raise InternalBotError('Не найдено административное сообщение с ключом {0}'.format(key))
        return QueryResult.parse_obj(record._mapping).text  # noqa: WPS437
