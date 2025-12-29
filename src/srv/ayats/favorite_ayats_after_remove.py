# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from collections.abc import Sequence
from typing import final, override

import attrs
from databases import Database

from app_types.listable import AsyncListable
from integrations.tg.fk_chat_id import ChatId
from srv.ayats.ayat import Ayat
from srv.ayats.ayat_identifier import AyatId
from srv.ayats.pg_ayat import PgAyat
from srv.ayats.text_len_shorten_ayat import TextLenSafeAyat


@final
@attrs.define(frozen=True)
class FavoriteAyatsAfterRemove(AsyncListable):
    """Избранные аяты."""

    _chat_id: ChatId
    _ayat_id: AyatId
    _pgsql: Database

    @override
    async def to_list(self) -> Sequence[Ayat]:
        """Получить избранные аяты.

        :returns: list[QAyat]
        """
        query = '\n'.join([
            'SELECT fa.ayat_id',
            'FROM favorite_ayats AS fa',
            'INNER JOIN users AS u ON fa.user_id = u.chat_id',
            'WHERE u.chat_id = :chat_id OR fa.ayat_id = :ayat_id',
            'ORDER BY fa.ayat_id',
        ])
        rows = await self._pgsql.fetch_all(
            query, {'chat_id': int(self._chat_id), 'ayat_id': self._ayat_id},
        )
        ayats = []
        flag = True
        for row in rows:
            if row['ayat_id'] > self._ayat_id and flag:
                ayats.append(TextLenSafeAyat(PgAyat.from_int(self._ayat_id, self._pgsql)))
                flag = False
            ayats.append(TextLenSafeAyat(PgAyat.from_int(row['ayat_id'], self._pgsql)))
        return ayats
