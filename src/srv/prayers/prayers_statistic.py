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
from typing import final
from itertools import batched

import attrs
from databases import Database
from pyeo import elegant


@final
@attrs.define(frozen=True)
@elegant
class PgPrayersStatisic(object):

    _pgsql: Database

    async def csv(self):
        query = """
            SELECT
              pau.is_read,
              p.day,
              p.name
            FROM prayers_at_user AS pau
            INNER JOIN prayers AS p ON pau.prayer_id = p.prayer_id
            WHERE pau.user_id = 358610865
            ORDER BY p.day, ARRAY_POSITION(ARRAY['fajr', 'dhuhr', 'asr', 'maghrib', 'isha''a']::text[], p.name::text)
        """
        prayers_per_day = batched(await self._pgsql.fetch_all(query), 5)
        res = ''
        res += "Day;fajr;dhuhr;asr;maghrib;isha'a\n"
        # print("Day;fajr;dhuhr;asr;maghrib;isha'a")
        for rows in prayers_per_day:
            res += str(rows[0]['day']) + ';'
            # print(rows[0]['day'], end=';')
            for row in rows:
                res += str(row['is_read']) + ';'
                # print(row['is_read'], end=';')
            res += '\n'
            # print()
        return res
