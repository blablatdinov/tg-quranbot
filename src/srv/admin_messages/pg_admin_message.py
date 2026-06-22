# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from exceptions.base_exception import InternalBotError
from srv.admin_messages.admin_message import AdminMessage


@final
@attrs.define(frozen=True)
class PgAdminMessage(AdminMessage):
    """Административное сообщение."""

    _key: str
    _pgsql: AsyncEngine

    @override
    async def to_str(self) -> str:
        """Текст административного сообщения.

        :raises InternalBotError: возбуждается если административное сообщение с переданным ключом не найдено
        :return: str
        """
        async with self._pgsql.connect() as conn:
            result = await conn.execute(
                text('SELECT text FROM admin_messages m WHERE m.key = :key'),
                {'key': self._key},
            )
            row = result.fetchone()
        if row is None:
            msg = 'Не найдено административное сообщение с ключом {0}'.format(self._key)
            raise InternalBotError(msg)
        return dict(row._mapping)['text']
