# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import uuid
from typing import final, override

import attrs
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app_types.intable import AsyncInt
from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.ayat_identifier import AyatId


@final
@attrs.define(frozen=True)
class AyatIdByPublicId(AsyncInt):
    """Поиск аятов по номеру суры, аята."""

    _public_id: uuid.UUID
    _pgsql: AsyncEngine

    @override
    async def to_int(self) -> AyatId:
        """Числовое представление.

        :return: int
        :raises AyatNotFoundError: если аят не найден
        """
        query = '\n'.join([
            'SELECT ayat_id FROM ayats',
            'WHERE public_id = :public_id',
        ])
        async with self._pgsql.connect() as conn:
            query_result = await conn.execute(text(query), {
                'public_id': str(self._public_id),
            })
            row = query_result.fetchone()
        if row is None:
            raise AyatNotFoundError
        return dict(row)['ayat_id']
