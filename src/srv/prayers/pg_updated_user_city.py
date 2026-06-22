# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from exceptions.internal_exceptions import UserNotFoundError
from integrations.tg.fk_chat_id import ChatId
from srv.prayers.city import City
from srv.prayers.updated_user_city import UpdatedUserCity


@final
@attrs.define(frozen=True)
class PgUpdatedUserCity(UpdatedUserCity):
    """Обновленный город у пользователя в БД postgres."""

    _city: City
    _chat_id: ChatId
    _pgsql: AsyncEngine

    @override
    async def update(self) -> None:
        """Обновление.

        :raises UserNotFoundError: незарегистрированный пользователь меняет город
        """
        query = '\n'.join([
            'UPDATE users',
            'SET city_id = :city_id',
            'WHERE chat_id = :chat_id',
            'RETURNING *',
        ])
        async with self._pgsql.connect() as conn:
            query_result = await conn.execute(text(query), {
                'city_id': str(await self._city.city_id()),
                'chat_id': int(self._chat_id),
            })
            rows = query_result.fetchall()
        if not rows:
            raise UserNotFoundError
