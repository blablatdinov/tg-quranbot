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
from typing import final, override

import attrs
import pytz

from app_types.update import Update
from integrations.tg.exceptions.update_parse_exceptions import MessageTextNotFoundError
from integrations.tg.message_text import MessageText
from srv.prayers.parsed_date import ParsedDate
from srv.prayers.prayer_date import PrayerDate


@final
@attrs.define(frozen=True)
class PrayersRequestDate(PrayerDate):
    """Дата намаза."""

    @override
    async def parse(self, update: Update) -> datetime.date:
        """Парсинг из текста сообщения.

        :param update: Update
        :return: datetime.date
        :raises ValueError: время намаза не соответствует формату
        """
        try:
            return await ParsedDate(
                MessageText(update),
            ).date()
        except (MessageTextNotFoundError, ValueError):
            return datetime.datetime.now(pytz.timezone('Europe/Moscow')).date()
