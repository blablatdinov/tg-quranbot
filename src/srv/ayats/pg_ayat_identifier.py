# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app_types.intable import AsyncInt
from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.ayat_identifier import AyatId, AyatIdentifier
from srv.ayats.search_query import AyatNum, SuraId


@final
@attrs.define(frozen=True)
class PgAyatIdentifier(AyatIdentifier):
    """Информация для идентификации аята."""

    _ayat_id: AsyncInt
    _pgsql: AsyncEngine

    @override
    async def ayat_id(self) -> AyatId:
        """Идентификатор в хранилище.

        :return: AyatId
        """
        return await self._ayat_id.to_int()

    @override
    async def sura_num(self) -> SuraId:
        """Номер суры.

        :return: SuraId
        :raises AyatNotFoundError: в случае если аят не найден
        """
        query = '\n'.join([
            'SELECT a.sura_id',
            'FROM ayats AS a',
            'WHERE a.ayat_id = :ayat_id',
        ])
        ayat_id = await self.ayat_id()
        async with self._pgsql.connect() as conn:
            query_result = await conn.execute(text(query), {'ayat_id': ayat_id})
            row = query_result.fetchone()
        if row is None:
            raise AyatNotFoundError
        return dict(row)['sura_id']

    @override
    async def ayat_num(self) -> AyatNum:
        """Номер аята.

        :return: AyatNum
        :raises AyatNotFoundError: в случае если аят не найден
        """
        query = '\n'.join([
            'SELECT ayat_number',
            'FROM ayats',
            'WHERE ayat_id = :ayat_id',
        ])
        ayat_id = await self.ayat_id()
        async with self._pgsql.connect() as conn:
            query_result = await conn.execute(text(query), {'ayat_id': ayat_id})
            row = query_result.fetchone()
        if row is None:
            raise AyatNotFoundError
        return dict(row)['ayat_number']
