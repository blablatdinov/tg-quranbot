from app_types.fk_async_int import FkAsyncInt
from app_types.listable import AsyncListable
from srv.users.PgUser import PgUser
from srv.users.pg_user import User


import attrs
from databases import Database
from pyeo import elegant


from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
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
            ','.join(list(map(str, self._chat_ids))),
        )
        rows = await self._pgsql.fetch_all(query)
        return [
            PgUser(FkAsyncInt(row['chat_id']), self._pgsql)
            for row in rows
        ]