from integrations.tg.chat_id import ChatId


import attrs
from databases import Database
from databases.interfaces import Record
from pyeo import elegant


import datetime
from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class ExistUserPrayers(object):
    """Существующие времена намаза у пользователя."""

    _pgsql: Database
    _chat_id: ChatId
    _date: datetime.date

    @override
    async def fetch(self) -> list[Record]:
        select_query = '\n'.join([
            'SELECT',
            '    pau.prayer_at_user_id,',
            '    pau.is_read',
            'FROM prayers_at_user AS pau',
            'INNER JOIN prayers AS p on pau.prayer_id = p.prayer_id',
            "WHERE p.day = :date AND pau.user_id = :chat_id AND p.name <> 'sunrise'",
            'ORDER BY pau.prayer_at_user_id',
        ])
        return await self._pgsql.fetch_all(select_query, {
            'date': self._date,
            'chat_id': int(self._chat_id),
        })