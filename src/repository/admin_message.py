from typing import Protocol

from databases import Database

from exceptions.base_exception import InternalBotError


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
