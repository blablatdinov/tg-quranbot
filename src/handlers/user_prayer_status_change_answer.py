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

import attrs
import httpx
from databases import Database
from pyeo import elegant

from app_types.intable import ThroughIntable
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.message_id import MessageId
from integrations.tg.tg_answers import TgAnswerToSender, TgKeyboardEditAnswer
from integrations.tg.tg_answers.interface import TgAnswer
from integrations.tg.tg_answers.markup_answer import TgAnswerMarkup
from integrations.tg.tg_answers.message_id_answer import TgMessageIdAnswer
from repository.prayer_time import PrayersWithoutSunrise, UserPrayers
from services.prayers.prayer_status import PrayerStatus, UserPrayerStatus
from services.prayers.user_prayer_date import UserPrayerDate
from services.user_prayer_keyboard import UserPrayersKeyboard


@final
@attrs.define(frozen=True)
@elegant
class UserPrayerStatusChangeAnswer(TgAnswer):
    """Ответ с изменением статуса прочитанности намаза."""

    _empty_answer: TgAnswer
    _pgsql: Database

    async def build(self, update) -> list[httpx.Request]:
        """Обработка запроса.

        :param update: Update
        :return: list[httpx.Request]
        """
        prayer_status = PrayerStatus(str(CallbackQueryData(update)))
        await UserPrayerStatus(self._pgsql).change(prayer_status)
        return await TgAnswerMarkup(
            TgMessageIdAnswer(
                TgAnswerToSender(
                    TgKeyboardEditAnswer(self._empty_answer),
                ),
                int(MessageId(update)),
            ),
            UserPrayersKeyboard(
                PrayersWithoutSunrise(UserPrayers(self._pgsql)),
                await UserPrayerDate(
                    ThroughIntable(prayer_status.user_prayer_id()),
                    self._pgsql,
                ).datetime(),
            ),
        ).build(update)
