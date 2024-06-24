from typing import final, override

import attrs
from databases import Database
from pyeo import elegant

from app_types.intable import AsyncInt


@final
@attrs.define(frozen=True)
@elegant
class ChatIdByLegacyId(AsyncInt):
    """Идентификатор чата по старому идентификатору в БД.

    Остались реферальные ссылки, сгенерированные на предыдущей версии бота
    """

    _pgsql: Database
    _legacy_id: AsyncInt

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
        return await self._pgsql.fetch_val(query, {'legacy_id': await self._legacy_id.to_int()})
