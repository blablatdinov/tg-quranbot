# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from databases import Database

from app_types.listable import AsyncListable
from srv.users.pg_user import PgUser
from srv.users.user import User


@final
@attrs.define(frozen=True)
class PgUsers(AsyncListable):
    """Пользователи из БД postgres."""

    _pgsql: Database
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
        rows = await self._pgsql.fetch_all(query)
        return [
            PgUser.int_ctor(row['chat_id'], self._pgsql)
            for row in rows
        ]
