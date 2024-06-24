from integrations.tg.chat_id import ChatId
from srv.prayers.ExistUserPrayersDict import ExistUserPrayersDict
from srv.prayers.exist_user_prayers import ExistUserPrayers


import attrs
from databases import Database
from pyeo import elegant


import datetime
from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class PgExistUserPrayers(ExistUserPrayers):
    """Существующие времена намаза у пользователя."""

    _pgsql: Database
    _chat_id: ChatId
    _date: datetime.date

    @override
    async def fetch(self) -> list[ExistUserPrayersDict]:
        """Получить.

        :return: list[Record]
        """
        select_query = '\n'.join([
            'SELECT',
            '    pau.prayer_at_user_id,',
            '    pau.is_read',
            'FROM prayers_at_user AS pau',
            'INNER JOIN prayers AS p on pau.prayer_id = p.prayer_id',
            "WHERE p.day = :date AND pau.user_id = :chat_id AND p.name <> 'sunrise'",
            'ORDER BY pau.prayer_at_user_id',
        ])
        return [
            {
                'prayer_at_user_id': record['prayer_at_user_id'],
                'is_read': record['is_read'],
            }
            for record in await self._pgsql.fetch_all(select_query, {
                'date': self._date,
                'chat_id': int(self._chat_id),
            })
        ]