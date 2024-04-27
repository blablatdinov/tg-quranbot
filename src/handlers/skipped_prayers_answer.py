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

import datetime
import enum
from copy import copy
from typing import Final, Protocol, final

import attrs
import httpx
import ujson
from databases import Database
from dateutil import rrule
from pyeo import elegant

from app_types.stringable import AsyncSupportsStr
from app_types.update import Update
from integrations.tg.chat_id import ChatId, TgChatId
from integrations.tg.keyboard import KeyboardInterface
from integrations.tg.tg_answers import TgAnswer, TgAnswerMarkup, TgAnswerToSender, TgMessageAnswer, TgTextAnswer
from services.user_prayer_keyboard import NewPrayersAtUser, PgNewPrayersAtUser
from srv.prayers.prayers_per_day import PgPrayersPerDay, PrayerPerDay, PrayersPerDay

IS_READ_LITERAL: Final = 'is_read'


class _PrayerNames(enum.Enum):

    fajr = ('fajr', 'Иртәнге')
    dhuhr = ('dhuhr', 'Өйлә')
    asr = ('asr', 'Икенде')
    maghrib = ('maghrib', 'Ахшам')
    isha = ("isha'a", 'Ястү')

    @classmethod
    def names(cls) -> tuple[str, ...]:
        return tuple(field.name for field in cls)


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
        return ujson.dumps({
            'inline_keyboard': [
                [{
                    'text': '{0}: (-1)'.format(field.value[1]),
                    'callback_data': 'decr({0})'.format(field.name),
                }]
                for field in _PrayerNames
            ],
        })


@elegant
class DatesRange(Protocol):
    """Диапазон дат."""

    async def range(self) -> list[datetime.date]:
        """Расчет диапазона."""


@final
@attrs.define(frozen=True)
@elegant
class PrayersDatesRange(DatesRange):
    """Диапазон дат намазов для пользователя."""

    _pgsql: Database
    _chat_id: ChatId

    async def range(self) -> list[datetime.date]:
        """Расчет диапазона.

        :return: list[datetim.date]
        """
        query = '\n'.join([
            'SELECT p.day',
            'FROM prayers_at_user AS pau',
            'INNER JOIN prayers AS p ON pau.prayer_id = p.prayer_id',
            'WHERE pau.user_id = :chat_id',
            "ORDER BY p.day, ARRAY_POSITION(ARRAY['fajr', 'dhuhr', 'asr', 'maghrib', 'isha''a']::text[], p.name::text)",
        ])
        rows = await self._pgsql.fetch_all(
            query,
            {'chat_id': int(self._chat_id)},
        )
        if not rows:
            return []
        return [
            dt.date()
            for dt in rrule.rrule(
                rrule.DAILY,
                dtstart=rows[0]['day'],
                until=rows[-1]['day'],
            )
        ]


@elegant
class PrayerStatistic(Protocol):

    async def statistic(self) -> dict: ...
    async def exists(self) -> bool: ...


@final
@attrs.define(frozen=True)
@elegant
class OneDayPrayerStatistic(PrayerStatistic):

    _origin: dict
    _date: datetime.date
    _prayer: tuple[PrayerPerDay, PrayerPerDay, PrayerPerDay, PrayerPerDay, PrayerPerDay]
    _prayers_at_user: NewPrayersAtUser

    async def statistic(self) -> dict:
        res = copy(self._origin)
        if await self.exists():
            # Prayer already exists for user
            for prayer_idx, prayer_name in enumerate(_PrayerNames.names()):
                res[prayer_name] += int(
                    not self._prayer[prayer_idx][IS_READ_LITERAL],
                )
        else:
            await self._prayers_at_user.create(self._date)
            for prayer_name in _PrayerNames.names():
                res[prayer_name] += 1
        return res

    async def exists(self) -> bool:
        return self._date == self._prayer[0]['day']


@final
@attrs.define(frozen=True)
@elegant
class PrayersStatistic(AsyncSupportsStr):
    """Статистика непрочитанных намазов."""

    _prayers_at_user: NewPrayersAtUser
    _chat_id: ChatId
    _pgsql: Database
    _prayers_per_day: PrayersPerDay
    _prayers_date_range: DatesRange

    async def to_str(self) -> str:
        """Приведение к строке.

        :return: str
        """
        idx = 0
        res = dict.fromkeys(_PrayerNames.names(), 0)
        prayers_per_day = await self._prayers_per_day.prayers()
        for date in await self._prayers_date_range.range():
            prayer_stat = OneDayPrayerStatistic(
                res,
                date,
                prayers_per_day[idx],
                self._prayers_at_user,
            )
            res = await prayer_stat.statistic()
            idx += int(await prayer_stat.exists())
        return '\n'.join([
            'Кол-во непрочитанных намазов:\n',
            'Иртәнге: {0}'.format(res[_PrayerNames.fajr.name]),
            'Өйлә: {0}'.format(res[_PrayerNames.dhuhr.name]),
            'Икенде: {0}'.format(res[_PrayerNames.asr.name]),
            'Ахшам: {0}'.format(res[_PrayerNames.maghrib.name]),
            'Ястү: {0}'.format(res[_PrayerNames.isha.name]),
        ])


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
        return await TgAnswerMarkup(
            TgTextAnswer(
                TgAnswerToSender(
                    TgMessageAnswer(self._empty_answer),
                ),
                PrayersStatistic(
                    PgNewPrayersAtUser(TgChatId(update), self._pgsql),
                    TgChatId(update),
                    self._pgsql,
                    PgPrayersPerDay(self._pgsql, TgChatId(update)),
                    PrayersDatesRange(self._pgsql, TgChatId(update)),
                ),
            ),
            SkippedPrayersKeyboard(),
        ).build(update)
