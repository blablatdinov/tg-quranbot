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
import json
import uuid
from typing import final, override

import attrs
from databases import Database
from databases.interfaces import Record
from pyeo import elegant

from app_types.update import Update
from integrations.tg.chat_id import TgChatId
from integrations.tg.message_text import MessageText
from services.answers.answer import KeyboardInterface
from srv.prayers.prayer_date import PrayerDate


@final
@attrs.define(frozen=True)
@elegant
class UserPrayersKeyboard(KeyboardInterface):
    """Клавиатура времен намаза."""

    _pgsql: Database
    _date: PrayerDate
    _chat_id: TgChatId

    @override
    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        :return: str
        """
        prayers = await self._exists_prayers(update)
        if not prayers:
            prayer_group_id = str(uuid.uuid4())
            await self._pgsql.fetch_val(
                'INSERT INTO prayers_at_user_groups VALUES (:prayer_group_id)', {'prayer_group_id': prayer_group_id},
            )
            query = """
                INSERT INTO prayers_at_user
                (user_id, prayer_id, is_read, prayer_group_id)
                SELECT
                    :chat_id,
                    p.prayer_id,
                    false,
                    :prayer_group_id
                FROM prayers AS p
                INNER JOIN cities AS c ON p.city_id = c.city_id
                INNER JOIN users AS u ON u.city_id = c.city_id
                WHERE p.day = :date AND u.chat_id = :chat_id AND p.name <> 'sunrise'
                ORDER BY
                    ARRAY_POSITION(ARRAY['fajr', 'dhuhr', 'asr', 'maghrib', 'isha''a']::text[], p.name::text)
            """
            await self._pgsql.execute(query, {
                'chat_id': int(self._chat_id),
                'prayer_group_id': prayer_group_id,
                'date': self._date.parse(str(MessageText(update))),
            })
            prayers = await self._exists_prayers(update)
        return json.dumps({
            'inline_keyboard': [[
                {
                    'text': '✅' if user_prayer['is_read'] else '❌',
                    'callback_data': ('mark_not_readed({0})' if user_prayer['is_read'] else 'mark_readed({0})').format(
                        user_prayer['prayer_at_user_id'],
                    ),
                }
                for user_prayer in prayers
            ]],
        })

    @override
    async def _exists_prayers(self, update: Update) -> list[Record]:
        select_query = """
            SELECT
                pau.prayer_at_user_id,
                pau.is_read
            FROM prayers_at_user AS pau
            INNER JOIN prayers AS p on pau.prayer_id = p.prayer_id
            WHERE p.day = :date AND pau.user_id = :chat_id AND p.name <> 'sunrise'
            ORDER BY pau.prayer_at_user_id
        """
        return await self._pgsql.fetch_all(select_query, {
            'date': self._date.parse(str(MessageText(update))),
            'chat_id': int(self._chat_id),
        })
