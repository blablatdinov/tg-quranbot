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
import enum
import json
from collections.abc import Generator
from itertools import batched
from typing import Final, final

import attrs
import httpx
from databases import Database
from dateutil import rrule
from pyeo import elegant

from app_types.update import Update
from integrations.tg.chat_id import ChatId, TgChatId
from integrations.tg.keyboard import KeyboardInterface
from integrations.tg.tg_answers import TgAnswer, TgAnswerMarkup, TgAnswerToSender, TgMessageAnswer, TgTextAnswer
from services.user_prayer_keyboard import NewPrayersAtUser, PgNewPrayersAtUser

IS_READ_LITERAL: Final = 'is_read'


class _PrayerNames(enum.Enum):

    fajr = 'fajr'
    dhuhr = 'dhuhr'
    asr = 'asr'
    maghrib = 'maghrib'
    isha = "isha'a"

    @classmethod
    def names(cls) -> tuple[str, ...]:
        return tuple(field.name for field in _PrayerNames)


@final
@attrs.define(frozen=True)
@elegant
class SkippedPrayersKeyboard(KeyboardInterface):
    """Клавиатура для пропущеных намазов."""

    async def generate(self, update: Update) -> str:
        """Генерация клавиатуры.

        :param update: Update
        :return: str
        """
        prayer_names = [
            'Иртәнге',
            'Өйлә',
            'Икенде',
            'Ахшам',
            'Ястү',
        ]
        return json.dumps({
            'inline_keyboard': [
                [{
                    'text': '{0}: (-1)'.format(prayer_name),
                    'callback_data': 'fk',
                }]
                for prayer_name in prayer_names
            ],
        })


@final
@attrs.define(frozen=True)
@elegant
class _PrayersStatistic(object):

    _prayers_at_user: NewPrayersAtUser
    _chat_id: ChatId
    _pgsql: Database

    async def statistic(self):
        idx = 0
        res = {
            prayer_name: 0
            for prayer_name in _PrayerNames.names()
        }
        prayers_per_day = await self._prayers_per_day()
        for date in await self._dates_range():
            if date == prayers_per_day[idx][0]['day']:
                for prayer_idx, prayer_name in enumerate(_PrayerNames.names()):
                    res[prayer_name] += int(not prayers_per_day[idx][prayer_idx][IS_READ_LITERAL])
                idx += 1
            else:
                await self._prayers_at_user.create(date)
                for prayer_name in _PrayerNames.names():
                    res[prayer_name] += 1
        return res

    async def _prayers_per_day(self) -> list[tuple]:
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
        return list(batched(
            await self._pgsql.fetch_all(query, {
                'chat_id': int(self._chat_id),
            }),
            5,
        ))

    async def _dates_range(self) -> Generator[datetime.date, None, None]:
        return (
            dt.date()
            for dt in rrule.rrule(
                rrule.DAILY,
                dtstart=datetime.date(2023, 10, 1),
                until=datetime.date(2023, 10, 31),
            )
        )


@final
@attrs.define(frozen=True)
@elegant
class SkippedPrayersAnswer(TgAnswer):
    """Пропущенные намазы."""

    _empty_answer: TgAnswer
    _pgsql: Database

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        prayers_statistic = await _PrayersStatistic(
            PgNewPrayersAtUser(TgChatId(update), self._pgsql),
            TgChatId(update),
            self._pgsql,
        ).statistic()
        return await TgAnswerMarkup(
            TgTextAnswer.str_ctor(
                TgAnswerToSender(
                    TgMessageAnswer(self._empty_answer),
                ),
                '\n'.join([
                    'Кол-во непрочитанных намазов:\n',
                    'Иртәнге: {0}'.format(prayers_statistic[_PrayerNames.fajr.name]),
                    'Өйлә: {0}'.format(prayers_statistic[_PrayerNames.dhuhr.name]),
                    'Икенде: {0}'.format(prayers_statistic[_PrayerNames.asr.name]),
                    'Ахшам: {0}'.format(prayers_statistic[_PrayerNames.maghrib.name]),
                    'Ястү: {0}'.format(prayers_statistic[_PrayerNames.isha.name]),
                ]),
            ),
            SkippedPrayersKeyboard(),
        ).build(update)
