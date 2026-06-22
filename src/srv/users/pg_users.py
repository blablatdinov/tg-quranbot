# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app_types.listable import AsyncListable
from srv.users.pg_user import PgUser
from srv.users.user import User


@final
@attrs.define(frozen=True)
class PgUsers(AsyncListable):
    """Пользователи из БД postgres."""

    _pgsql: AsyncEngine
    _chat_ids: list[int]

    @override
    async def to_list(self) -> list[User]:
        """Список пользователей.

        :return: list[User]
        """
        if not self._chat_ids:
            return []
        query_template = '\n'.join([
            'SELECT chat_id',
            'FROM users',
            'WHERE chat_id IN ({0})',
        ])
        query = query_template.format(
            ','.join([str(elem) for elem in self._chat_ids]),
        )
        async with self._pgsql.connect() as conn:
            query_result = await conn.execute(text(query))
            rows = query_result.fetchall()
        return [
            PgUser.int_ctor(dict(row)['chat_id'], self._pgsql)
            for row in rows
        ]
