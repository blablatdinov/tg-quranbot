from integrations.tg.chat_id import ChatId
from srv.prayers.new_prayers_at_user import NewPrayersAtUser


import attrs
from databases import Database
from pyeo import elegant


import datetime
import uuid
from typing import final


@final
@attrs.define(frozen=True)
@elegant
class PgNewPrayersAtUser(NewPrayersAtUser):
    """Новые записи о статусе намаза."""

    _chat_id: ChatId
    _pgsql: Database

    async def create(self, date: datetime.date) -> None:
        """Создать.

        :param date: datetime.date
        """
        # TODO: must fail on not create
        prayer_group_id = str(uuid.uuid4())
        await self._pgsql.fetch_val(
            'INSERT INTO prayers_at_user_groups VALUES (:prayer_group_id)', {'prayer_group_id': prayer_group_id},
        )
        query = '\n'.join([
            'INSERT INTO prayers_at_user',
            '(user_id, prayer_id, is_read, prayer_group_id)',
            'SELECT',
            '    :chat_id,',
            '    p.prayer_id,',
            '    false,',
            '    :prayer_group_id',
            'FROM prayers AS p',
            'INNER JOIN cities AS c ON p.city_id = c.city_id',
            'INNER JOIN users AS u ON u.city_id = c.city_id',
            "WHERE p.day = :date AND u.chat_id = :chat_id AND p.name <> 'sunrise'",
            'ORDER BY',
            "    ARRAY_POSITION(ARRAY['fajr', 'dhuhr', 'asr', 'maghrib', 'isha''a']::text[], p.name::text)",
        ])
        await self._pgsql.execute(query, {
            'chat_id': int(self._chat_id),
            'prayer_group_id': prayer_group_id,
            'date': date,
        })