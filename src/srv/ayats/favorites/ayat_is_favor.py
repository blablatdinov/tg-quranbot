# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from databases import Database

from app_types.async_supports_bool import AsyncSupportsBool
from integrations.tg.fk_chat_id import ChatId
from srv.ayats.ayat import Ayat


@final
@attrs.define(frozen=True)
class AyatIsFavor(AsyncSupportsBool):
    """Является ли аят избранным."""

    _ayat: Ayat
    _chat_id: ChatId
    _pgsql: Database

    @override
    async def to_bool(self) -> bool:
        """Приведение к булевому значению.

        :return: bool
        """
        query = '\n'.join([
            'SELECT COUNT(*)',
            'FROM favorite_ayats AS fa',
            'INNER JOIN users AS u ON fa.user_id = u.chat_id',
            'WHERE fa.ayat_id = :ayat_id AND u.chat_id = :chat_id',
        ])
        count = await self._pgsql.fetch_val(
            query, {'ayat_id': await self._ayat.identifier().ayat_id(), 'chat_id': self._chat_id},
        )
        return bool(count)
