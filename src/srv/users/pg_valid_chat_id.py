# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import SupportsInt, final, override

import attrs
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app_types.fk_async_int import FkAsyncInt
from app_types.intable import AsyncInt
from exceptions.internal_exceptions import UserNotFoundError
from srv.users.valid_chat_id import ValidChatId


@final
@attrs.define(frozen=True)
class PgValidChatId(ValidChatId):
    """Проверенный идентификатор чата в БД postgres."""

    _pgsql: AsyncEngine
    _unreliable: AsyncInt

    @classmethod
    def int_ctor(cls, pgsql: AsyncEngine, int_value: SupportsInt) -> ValidChatId:
        """Числовой конструктор.

        :param pgsql: AsyncEngine
        :param int_value: SupportsInt
        :return: ValidChatId
        """
        return cls(pgsql, FkAsyncInt(int_value))

    @override
    async def to_int(self) -> int:
        """Числовое представление.

        :return: int
        :raises UserNotFoundError: если пользователь не найден
        """
        async with self._pgsql.connect() as conn:
            result = await conn.execute(
                text('\n'.join([
                    'SELECT chat_id',
                    'FROM users',
                    'WHERE chat_id = :chat_id',
                ])),
                {'chat_id': await self._unreliable.to_int()},
            )
            row = result.fetchone()
        if row is None:
            raise UserNotFoundError
        return row[0]
