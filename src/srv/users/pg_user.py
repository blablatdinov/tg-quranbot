# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from typing import final, override

import attrs
from databases import Database

from app_types.intable import AsyncInt
from exceptions.internal_exceptions import UserNotFoundError
from srv.users.chat_id_by_legacy_id import ChatIdByLegacyId
from srv.users.pg_valid_chat_id import PgValidChatId
from srv.users.user import User
from srv.users.valid_chat_id import ValidChatId


@final
@attrs.define(frozen=True)
class PgUser(User):
    """Пользователь в БД postgres."""

    _chat_id: ValidChatId
    _pgsql: Database

    @classmethod
    def legacy_id_ctor(cls, legacy_id: AsyncInt, pgsql: Database) -> User:
        """Конструктор по старому идентификатору в БД.

        :param legacy_id: int
        :param pgsql: Database
        :return: User
        """
        return cls(PgValidChatId(pgsql, ChatIdByLegacyId(pgsql, legacy_id)), pgsql)

    @classmethod
    def int_ctor(cls, chat_id: int, pgsql: Database) -> User:
        """Конструктор по идентификатору чата.

        :param chat_id: int
        :param pgsql: Database
        :return: User
        """
        return cls(PgValidChatId.int_ctor(pgsql, chat_id), pgsql)

    @override
    async def chat_id(self) -> int:
        """Идентификатор чата.

        :return: int
        """
        return await self._chat_id.to_int()

    @override
    async def day(self) -> int:
        """День для рассылки утреннего контента.

        :return: int
        """
        query = '\n'.join([
            'SELECT day',
            'FROM users',
            'WHERE chat_id = :chat_id',
        ])
        query_result = await self._pgsql.fetch_val(
            query,
            {'chat_id': await self._chat_id.to_int()},
        )
        if not query_result:
            raise UserNotFoundError
        return query_result

    @override
    async def is_active(self) -> bool:
        """Статус пользователя.

        :return: bool
        """
        query = '\n'.join([
            'SELECT is_active',
            'FROM users',
            'WHERE chat_id = :chat_id',
        ])
        query_result = await self._pgsql.fetch_val(
            query,
            {'chat_id': await self._chat_id.to_int()},
        )
        if not query_result:
            raise UserNotFoundError
        return query_result
