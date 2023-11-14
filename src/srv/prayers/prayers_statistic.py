"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import datetime
from typing import final, TypedDict
from itertools import batched

import attrs
from databases import Database
from pyeo import elegant

from integrations.tg.chat_id import ChatId

_PrayerStatisticRow = TypedDict(
    '_PrayerStatisticRow',
    {
        'asr': bool,
        'day': datetime.date,
        'dhuhr': bool,
        'fajr': bool,
        "isha'a": bool,
        'maghrib': bool,
    }
)


@final
@attrs.define(frozen=True)
@elegant
class PgPrayersStatisic(object):

    _pgsql: Database
    _chat_id: ChatId

    async def generate(self) -> list[_PrayerStatisticRow]:
        query = """
            SELECT
                pau.is_read,
                p.day,
                p.name
            FROM prayers_at_user AS pau
            INNER JOIN prayers AS p ON pau.prayer_id = p.prayer_id
            WHERE pau.user_id = :chat_id
            ORDER BY p.day, ARRAY_POSITION(ARRAY['fajr', 'dhuhr', 'asr', 'maghrib', 'isha''a']::text[], p.name::text)
        """
        prayers_per_day = batched(
            await self._pgsql.fetch_all(query, {
                'chat_id': int(self._chat_id),
            }),
            5,
        )
        res = []
        for rows in prayers_per_day:
            statistic_row: _PrayerStatisticRow = {
                'day': rows[0]['day'],
                'fajr': rows[0]['is_read'],
                'dhuhr': rows[1]['is_read'],
                'asr': rows[2]['is_read'],
                'maghrib': rows[3]['is_read'],
                "isha'a": rows[4]['is_read'],
            }
            res.append(statistic_row)
        return res
