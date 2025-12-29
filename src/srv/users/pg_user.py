# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
        if query_result is None:
            raise UserNotFoundError
        return query_result
