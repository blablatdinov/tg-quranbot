from app_types.stringable import AsyncSupportsStr
from exceptions.content_exceptions import UserHasNotCityIdError
from integrations.tg.chat_id import ChatId


import attrs
from databases import Database
from pyeo import elegant


from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class UserCityId(AsyncSupportsStr):
    """Идентификатор города."""

    _pgsql: Database
    _chat_id: ChatId

    @override
    async def to_str(self) -> str:
        """Строковое представление.

        :return: str
        :raises UserHasNotCityIdError: user has not set city
        """
        query = '\n'.join([
            'SELECT c.city_id',
            'FROM cities AS c',
            'INNER JOIN users AS u ON u.city_id = c.city_id',
            'WHERE u.chat_id = :chat_id',
        ])
        city_name = await self._pgsql.fetch_val(query, {'chat_id': int(self._chat_id)})
        if not city_name:
            raise UserHasNotCityIdError
        return city_name