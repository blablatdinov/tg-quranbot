# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from databases import Database

from exceptions.base_exception import InternalBotError
from srv.admin_messages.admin_message import AdminMessage


@final
@attrs.define(frozen=True)
class PgAdminMessage(AdminMessage):
    """Административное сообщение."""

    _key: str
    _pgsql: Database

    @override
    async def to_str(self) -> str:
        """Текст административного сообщения.

        :raises InternalBotError: возбуждается если административное сообщение с переданным ключом не найдено
        :return: str
        """
        record = await self._pgsql.fetch_one(
            'SELECT text FROM admin_messages m WHERE m.key = :key', {'key': self._key},
        )
        if not record:
            msg = 'Не найдено административное сообщение с ключом {0}'.format(self._key)
            raise InternalBotError(msg)
        return record['text']
