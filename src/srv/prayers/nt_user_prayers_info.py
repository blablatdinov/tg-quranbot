# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

import datetime
from contextlib import suppress
from typing import final, override

import attrs
import pytz
from databases import Database

from exceptions.internal_exceptions import PrayerAtUserAlreadyExistsError
from integrations.tg.fk_chat_id import ChatId
from srv.prayers.pg_new_prayers_at_user import PgNewPrayersAtUser
from srv.prayers.prayers_info import PrayerMessageTextDict, PrayersInfo


@final
@attrs.define(frozen=True)
class NtUserPrayersInfo(PrayersInfo):
    """Декоратор для создания записи о времени намаза в таблице prayers_at_user."""

    _origin: PrayersInfo
    _pgsql: Database
    _chat_id: ChatId

    @override
    async def to_dict(self) -> PrayerMessageTextDict:
        """Словарь с данными для отправки пользователю."""
        origin = await self._origin.to_dict()
        day = (
            datetime.datetime
            .strptime(origin['date'], '%d.%m.%Y')
            .replace(tzinfo=pytz.timezone('Europe/Moscow'))
            .date()
        )
        with suppress(PrayerAtUserAlreadyExistsError):
            await PgNewPrayersAtUser(int(self._chat_id), self._pgsql).create(day)
        return origin
