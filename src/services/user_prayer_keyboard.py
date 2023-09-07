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
import json
import uuid
from typing import final

import attrs
from databases import Database
from pyeo import elegant

from app_types.update import Update
from integrations.tg.chat_id import TgChatId
from repository.user_prayers_interface import UserPrayersInterface
from services.answers.answer import KeyboardInterface
from services.user_prayer_button_callback import UserPrayersButtonCallback


@final
@attrs.define(frozen=True)
@elegant
class UserPrayersKeyboardByChatId(KeyboardInterface):
    """Клавиатура времен намаза с идентификатором чата в конструкторе."""

    _user_prayer_times: UserPrayersInterface
    _date: datetime.date
    _chat_id: int

    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        :return: str
        """
        return json.dumps({
            'inline_keyboard': [[
                {
                    'text': '✅' if user_prayer.is_readed else '❌',
                    'callback_data': str(UserPrayersButtonCallback(user_prayer)),
                }
                for user_prayer in await self._user_prayer_times.prayer_times(self._chat_id, self._date)
            ]],
        })


@final
@attrs.define(frozen=True)
@elegant
class UserPrayersKeyboard(KeyboardInterface):
    """Клавиатура времен намаза."""

    _pgsql: Database
    _date: datetime.date
    _chat_id: TgChatId

    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        :return: str
        """
        print('!!!', self._date, type(self._date))
        prayers = await self._exists_prayers()
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
                ORDER BY p.name
            """
            await self._pgsql.execute(query, {
                'chat_id': int(self._chat_id),
                'prayer_group_id': prayer_group_id,
                'date': self._date,
            })
            prayers = await self._exists_prayers()
        print('!!!', [
            dict(row._mapping)
            for row in await self._pgsql.fetch_all("""
                SELECT
                    p.day
                FROM prayers AS p
                INNER JOIN cities AS c ON p.city_id = c.city_id
                WHERE p.city_id = '080fd3f4-678e-4a1c-97d2-4460700fe7ac' AND p.day = :date
                ORDER BY p.name
            """, {'date': self._date})
        ])
        print('!!!', [
            dict(row._mapping)
            for row in await self._pgsql.fetch_all('SELECT * FROM prayers_at_user')
        ])
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

    async def _exists_prayers(self):
        select_query = """
            SELECT
                pau.prayer_at_user_id,
                pau.is_read
            FROM prayers_at_user AS pau
            INNER JOIN prayers AS p on pau.prayer_id = p.prayer_id
            WHERE p.day = :date AND pau.user_id = :chat_id AND p.name <> 'sunrise'
            ORDER BY pau.prayer_at_user_id
        """
        prayers = await self._pgsql.fetch_all(select_query, {
            'date': self._date,
            'chat_id': int(self._chat_id),
        })
        return prayers
