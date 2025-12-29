# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
