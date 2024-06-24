from typing import SupportsInt, final, override

import attrs
from databases import Database
from pyeo import elegant

from app_types.fk_async_int import FkAsyncInt
from app_types.intable import AsyncInt
from exceptions.internal_exceptions import UserNotFoundError
from srv.users.valid_chat_id import ValidChatId


@final
@attrs.define(frozen=True)
@elegant
class PgValidChatId(ValidChatId):
    """Проверенный идентификатор чата в БД postgres."""

    _pgsql: Database
    _unreliable: AsyncInt

    @classmethod
    def int_ctor(cls, pgsql: Database, int_value: SupportsInt) -> ValidChatId:
        """Числовой конструктор.

        :param pgsql: Database
        :param int_value: SupportsInt
        :return: FkValidChatId
        """
        return cls(pgsql, FkAsyncInt(int_value))

    @override
    async def to_int(self) -> int:
        """Числовое представление.

        :return: int
        :raises UserNotFoundError: если пользователь не найден
        """
        chat_id = await self._pgsql.fetch_val(
            '\n'.join([
                'SELECT chat_id',
                'FROM users',
                'WHERE chat_id = :chat_id',
            ]),
            {'chat_id': await self._unreliable.to_int()},
        )
        if not chat_id:
            raise UserNotFoundError
        return chat_id
