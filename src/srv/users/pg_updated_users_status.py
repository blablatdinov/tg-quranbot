# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from databases import Database

from app_types.listable import AsyncListable
from srv.users.updated_users_status import UpdatedUsersStatus
from srv.users.user import User


@final
@attrs.define(frozen=True)
class PgUpdatedUsersStatus(UpdatedUsersStatus):
    """Обновление статусов пользователей."""

    _pgsql: Database
    _users: AsyncListable[User]

    @override
    async def update(self, to: bool) -> None:
        """Обновление.

        :param to: bool
        """
        query_template = '\n'.join([
            'UPDATE users',
            'SET is_active = :to',
            'WHERE chat_id in ({0})',
        ])
        users = await self._users.to_list()
        if not users:
            return
        query = query_template.format(','.join([
            str(await user.chat_id())
            for user in users
        ]))
        await self._pgsql.execute(query, {'to': to})
