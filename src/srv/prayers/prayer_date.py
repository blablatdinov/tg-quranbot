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
from contextlib import suppress
from typing import Protocol, final, override

import attrs
import pytz
from databases import Database
from pyeo import elegant

from app_types.update import Update
from integrations.tg.exceptions.update_parse_exceptions import MessageTextNotFoundError
from integrations.tg.message_text import MessageText
from srv.prayers.prayer_status import PrayerStatus


@elegant
class PrayerDate(Protocol):
    """Дата времен намаза."""

    async def parse(self, update: Update) -> datetime.date:
        """Парсинг из текста сообщения.

        :param update: Update
        """


@final
@attrs.define(frozen=True)
@elegant
class FkPrayerDate(PrayerDate):
    """Фейковая дата времен намаза."""

    _origin: datetime.date

    @override
    async def parse(self, update: Update) -> datetime.date:
        """Парсинг из текста сообщения.

        :param update: Update
        :return: datetime.date
        """
        return self._origin


@final
@attrs.define(frozen=True)
@elegant
class PrayersRequestDate(PrayerDate):
    """Дата намаза."""

    @override
    async def parse(self, update: Update) -> datetime.date:
        """Парсинг из текста сообщения.

        :param update: Update
        :return: datetime.date
        :raises ValueError: время намаза не соответствует формату
        """
        date = str(MessageText(update)).split(' ')[-1]
        if date == 'намаза':
            return datetime.datetime.now(pytz.timezone('Europe/Moscow')).date()
        formats = ('%d.%m.%Y', '%d-%m-%Y')  # noqa: WPS323 not string formatting
        for fmt in formats:
            with suppress(ValueError):
                return datetime.datetime.strptime(date, fmt).date()
        msg = "time data '{0}' does not match formats {1}".format(date, formats)
        raise ValueError(msg)


@final
@attrs.define(frozen=True)
@elegant
class MessageHasNotTextSafeDate(PrayerDate):
    """Декоратор для обработки update без текста сообщеиня.

    Почему-то телеграм не присылает текст сообщения спустя время
    """

    _origin: PrayerDate
    _pgsql: Database

    @override
    async def parse(self, update: Update) -> datetime.date:
        """Парсинг из текста сообщения.

        :param update: Update
        :return: datetime.date
        """
        try:
            return await self._origin.parse(update)
        except MessageTextNotFoundError:
            query = """
                SELECT prayers.day
                FROM prayers_at_user
                INNER JOIN prayers ON prayers_at_user.prayer_id = prayers.prayer_id
                WHERE prayer_at_user_id = :prayer_at_user_id
            """
            return await self._pgsql.fetch_val(query, {
                'prayer_at_user_id': PrayerStatus.update_ctor(update).user_prayer_id(),
            })


@final
@attrs.define(frozen=True)
@elegant
class PrayersMarkAsDate(PrayerDate):
    """Дата намаза при редактировании."""

    @override
    async def parse(self, update: Update) -> datetime.date:
        """Парсинг из текста сообщения.

        :param update: Update
        :return: datetime.date
        """
        msg_first_line = str(MessageText(update)).split('\n')[0]
        date = msg_first_line.split(' ')[-1][1:-1]
        return datetime.datetime.strptime(date, '%d.%m.%Y').date()  # noqa: WPS323 not string formatting
