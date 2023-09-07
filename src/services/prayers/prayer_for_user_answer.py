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
from typing import final

import attrs
import httpx
import pytz
from databases import Database
from pyeo import elegant

from app_types.update import Update
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers import TgAnswer, TgAnswerMarkup, TgTextAnswer
from repository.user_prayers_interface import UserPrayersInterface
from services.user_prayer_keyboard import UserPrayersKeyboard


@final
@attrs.define(frozen=True)
@elegant
class PrayerForUserAnswer(TgAnswer):
    """Ответ пользователю с временами намаза."""

    _pgsql: Database
    _origin: TgAnswer
    _user_prayers: UserPrayersInterface

    async def build(self, update: Update) -> list[httpx.Request]:
        """Отправить.

        :param update: Update
        :return: list[types.Message]
        """
        prayers = await self._user_prayers.prayer_times(
            int(TgChatId(update)),
            datetime.datetime.now(pytz.timezone('Europe/Moscow')).date(),
        )
        time_format = '%H:%M'
        template = '\n'.join([
            'Время намаза для г. {city_name} ({date})\n',
            'Иртәнге: {fajr_prayer_time}',
            'Восход: {sunrise_prayer_time}',
            'Өйлә: {dhuhr_prayer_time}',
            'Икенде: {asr_prayer_time}',
            'Ахшам: {magrib_prayer_time}',
            'Ястү: {ishaa_prayer_time}',
        ])
        return await TgAnswerMarkup(
            TgTextAnswer(
                self._origin,
                template.format(
                    city_name=prayers[0].city,
                    date=prayers[0].day.strftime('%d.%m.%Y'),
                    fajr_prayer_time=prayers[0].time.strftime(time_format),
                    sunrise_prayer_time=prayers[1].time.strftime(time_format),
                    dhuhr_prayer_time=prayers[2].time.strftime(time_format),
                    asr_prayer_time=prayers[3].time.strftime(time_format),
                    magrib_prayer_time=prayers[4].time.strftime(time_format),
                    ishaa_prayer_time=prayers[5].time.strftime(time_format),
                ),
            ),
            UserPrayersKeyboard(
                self._pgsql,
                datetime.datetime.now(pytz.timezone('Europe/Moscow')).date(),
                TgChatId(update),
            ),
        ).build(update)
