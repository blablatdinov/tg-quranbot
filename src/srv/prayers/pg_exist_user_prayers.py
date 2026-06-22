# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from typing import final, override

import attrs
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from integrations.tg.fk_chat_id import ChatId
from srv.prayers.exist_user_prayers import ExistUserPrayers
from srv.prayers.exist_user_prayers_dict import ExistUserPrayersDict


@final
@attrs.define(frozen=True)
class PgExistUserPrayers(ExistUserPrayers):
    """Существующие времена намаза у пользователя."""

    _pgsql: AsyncEngine
    _chat_id: ChatId
    _date: datetime.date

    @override
    async def fetch(self) -> list[ExistUserPrayersDict]:
        """Получить.

        :return: list[Record]
        """
        select_query = '\n'.join([
            'SELECT',
            '    pau.prayer_at_user_id,',
            '    pau.is_read',
            'FROM prayers_at_user AS pau',
            'INNER JOIN prayers AS p on pau.prayer_id = p.prayer_id',
            "WHERE p.day = :date AND pau.user_id = :chat_id AND p.name <> 'sunrise'",
            'ORDER BY pau.prayer_at_user_id',
        ])
        async with self._pgsql.connect() as conn:
            query_result = await conn.execute(text(select_query), {
                'date': self._date,
                'chat_id': int(self._chat_id),
            })
            rows = query_result.fetchall()
        return [
            {
                'prayer_at_user_id': dict(row)['prayer_at_user_id'],
                'is_read': dict(row)['is_read'],
            }
            for row in rows
        ]
