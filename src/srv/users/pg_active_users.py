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
class PgActiveUsers(AsyncListable):
    """Активные пользователи."""

    _pgsql: AsyncEngine

    @override
    async def to_list(self) -> list[User]:
        """Список пользователей.

        :return: list[User]
        """
        query = '\n'.join([
            'SELECT chat_id',
            'FROM users',
            "WHERE is_active = 't'",
        ])
        async with self._pgsql.connect() as conn:
            query_result = await conn.execute(text(query))
            rows = query_result.mappings().fetchall()
        return [
            PgUser.int_ctor(row['chat_id'], self._pgsql)
            for row in rows
        ]
