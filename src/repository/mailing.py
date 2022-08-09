from aiogram import types
from asyncpg import Connection
from pydantic import BaseModel

from repository.update_log import UpdatesLogRepositoryInterface


class _ReturningIdResult(BaseModel):

    id: int


class MailingRepository(object):
    """Класс для работы с хранилищем рассылок."""

    def __init__(self, connection: Connection, messages_repository: UpdatesLogRepositoryInterface):
        self._connection = connection
        self._messages_repository = messages_repository

    async def create_mailing(self, messages: list[types.Message]) -> int:
        """Создать рассылку.

        :param messages: list[types.Message]
        :return: int
        """
        query = "INSERT INTO bot_init_mailing (id, is_cleaned) values (default, 'f') RETURNING id"
        row = await self._connection.fetchrow(query)
        mailing_id = _ReturningIdResult.parse_obj(row).id
        await self._messages_repository.bulk_save_messages(messages, mailing_id)
        return mailing_id
