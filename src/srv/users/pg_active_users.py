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

from app_types.listable import AsyncListable
from srv.users.pg_user import PgUser
from srv.users.user import User


@final
@attrs.define(frozen=True)
class PgActiveUsers(AsyncListable):
    """Активные пользователи."""

    _pgsql: Database

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
        rows = await self._pgsql.fetch_all(query)
        return [
            PgUser.int_ctor(row['chat_id'], self._pgsql)
            for row in rows
        ]
