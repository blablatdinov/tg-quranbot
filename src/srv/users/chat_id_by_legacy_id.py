# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from databases import Database

from app_types.fk_async_int import FkAsyncInt
from app_types.intable import AsyncInt
from exceptions.internal_exceptions import UserNotFoundError


@final
@attrs.define(frozen=True)
class ChatIdByLegacyId(AsyncInt):
    """Идентификатор чата по старому идентификатору в БД.

    Остались реферальные ссылки, сгенерированные на предыдущей версии бота
    """

    _pgsql: Database
    _legacy_id: AsyncInt

    @classmethod
    def int_ctor(cls, database: Database, legacy_id: int) -> AsyncInt:
        """Конструктор для legacy_id в формате числа."""
        return cls(database, FkAsyncInt(legacy_id))

    @override
    async def to_int(self) -> int:
        """Числовое представление.

        :return: int
        """
        query = '\n'.join([
            'SELECT chat_id',
            'FROM users',
            'WHERE legacy_id = :legacy_id',
        ])
        query_result = await self._pgsql.fetch_val(
            query,
            {'legacy_id': await self._legacy_id.to_int()},
        )
        if not query_result:
            raise UserNotFoundError
        return query_result
