# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app_types.async_supports_str import AsyncSupportsStr
from exceptions.content_exceptions import UserHasNotCityIdError
from integrations.tg.fk_chat_id import ChatId


@final
@attrs.define(frozen=True)
class UserCityId(AsyncSupportsStr):
    """Идентификатор города."""

    _pgsql: AsyncEngine
    _chat_id: ChatId

    @override
    async def to_str(self) -> str:
        """Строковое представление.

        :return: str
        :raises UserHasNotCityIdError: user has not set city
        """
        query = '\n'.join([
            'SELECT c.city_id',
            'FROM cities AS c',
            'INNER JOIN users AS u ON u.city_id = c.city_id',
            'WHERE u.chat_id = :chat_id',
        ])
        async with self._pgsql.connect() as conn:
            query_result = await conn.execute(
                text(query), {'chat_id': int(self._chat_id)},
            )
            row = query_result.fetchone()
        if row is None:
            raise UserHasNotCityIdError
        return row[0]
