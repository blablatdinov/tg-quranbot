# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from typing import final, override

import attrs
from databases import Database
from pyeo import elegant

from app_types.update import Update
from integrations.tg.chat_id import ChatId
from services.answers.answer import KeyboardInterface
from srv.prayers.exist_user_prayers import ExistUserPrayers
from srv.prayers.prayer_date import PrayerDate


@final
@attrs.define(frozen=True)
@elegant
class PrayersProtectDouble(KeyboardInterface):
    """Предохранитель от дублей во временах намаза."""

    _origin: KeyboardInterface
    _pgsql: Database
    _chat_id: ChatId
    _date: PrayerDate

    @override
    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        :return: str
        :raises ValueError: Пользователь запросил времена дважды
        """
        exist_prayers = ExistUserPrayers(self._pgsql, self._chat_id, await self._date.parse(update))
        async with self._pgsql.transaction():
            origin_val = await self._origin.generate(update)
            expected_prayers_count = 5
            if len(await exist_prayers.fetch()) > expected_prayers_count:
                msg = 'Prayers doubled'
                raise ValueError(msg)
        return origin_val
