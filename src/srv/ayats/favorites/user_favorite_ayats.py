# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from databases import Database

from app_types.listable import AsyncListable
from integrations.tg.fk_chat_id import ChatId
from srv.ayats.ayat import Ayat
from srv.ayats.pg_ayat import PgAyat
from srv.ayats.text_len_shorten_ayat import TextLenSafeAyat


@final
@attrs.define(frozen=True)
class UserFavoriteAyats(AsyncListable[Ayat]):
    """Избранные аяты пользователя."""

    _pgsql: Database
    _chat_id: ChatId

    @override
    async def to_list(self) -> list[Ayat]:
        """Списковое представление.

        :return: list[PgAyat]
        """
        query = '\n'.join([
            'SELECT a.ayat_id AS id',
            'FROM favorite_ayats AS fa',
            'INNER JOIN ayats AS a ON fa.ayat_id = a.ayat_id',
            'INNER JOIN users AS u ON fa.user_id = u.chat_id',
            'WHERE u.chat_id = :chat_id',
            'ORDER BY a.ayat_id',
        ])
        rows = await self._pgsql.fetch_all(query, {'chat_id': int(self._chat_id)})
        return [
            TextLenSafeAyat(PgAyat.from_int(row['id'], self._pgsql)) for row in rows
        ]
