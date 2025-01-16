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

from typing import final, override

import attrs
import httpx
from databases import Database
from redis.asyncio import Redis

from app_types.logger import LogSink
from app_types.update import Update
from handlers.pg_prayer_time_answer import PgPrayerTimeAnswer
from integrations.tg.tg_answers.tg_answer import TgAnswer
from settings import Settings
from srv.prayers.prayer_status import PrayerStatus
from srv.prayers.user_prayer_status import UserPrayerStatus


@final
@attrs.define(frozen=True)
class UserPrayerStatusChangeAnswer(TgAnswer):
    """Ответ с изменением статуса прочитанности намаза."""

    _empty_answer: TgAnswer
    _pgsql: Database
    _redis: Redis
    _logger: LogSink
    _settings: Settings

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Обработка запроса.

        :param update: Update
        :return: list[httpx.Request]
        """
        prayer_status = PrayerStatus.update_ctor(update)
        await UserPrayerStatus(self._pgsql).change(prayer_status)
        return await PgPrayerTimeAnswer.edited_markup_ctor(
            self._pgsql,
            self._empty_answer,
            [123],
            self._redis,
            self._logger,
            self._settings,
        ).build(update)
