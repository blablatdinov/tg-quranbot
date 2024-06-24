from typing import final, override

import attrs
from databases import Database
from pyeo import elegant

from app_types.listable import AsyncListable
from srv.users.updated_users_status import UpdatedUsersStatus
from srv.users.user import User


@final
@attrs.define(frozen=True)
@elegant
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
