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


class AdminMessageInterface(Protocol):
    """Интерфейс административного сообщения."""

    async def text(self) -> str:
        """Чтение содержимого административного сообщения."""


class AdminMessage(AdminMessageInterface):
    """Административное сообщение."""

    def __init__(self, key: str, connection: Database):
        """Конструктор класса.

        :param key: str
        :param connection: Database
        """
        self._key = key
        self._connection = connection

    async def text(self) -> str:
        """Текст административного сообщения.

        :raises InternalBotError: возбуждается если административное сообщение с переданным ключом не найдено
        :return: str
        """
        record = await self._connection.fetch_one(
            'SELECT text FROM admin_messages m WHERE m.key = :key', {'key': self._key},
        )
        if not record:
            raise InternalBotError('Не найдено административное сообщение с ключом {0}'.format(self._key))
        return record._mapping['text']  # noqa: WPS437


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
