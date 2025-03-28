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

from app_types.async_date import AsyncDate
from app_types.stringable import SupportsStr


@final
@attrs.define(frozen=True)
class ParsedDate(AsyncDate):
    """Дата намаза."""

    _msg_text: SupportsStr

    @override
    async def date(self) -> datetime.date:
        """Спарсить дату из сообщения."""
        date = str(self._msg_text).rsplit(' ', maxsplit=1)[-1]
        formats = ('%d.%m.%Y', '%d-%m-%Y')  # noqa: WPS323 not string formatting
        for fmt in formats:
            with suppress(ValueError):
                return datetime.datetime.strptime(date, fmt).astimezone(
                    pytz.timezone('Europe/Moscow'),
                ).date()
        msg = "time data '{0}' does not match formats {1}".format(date, formats)
        # TODO #1428:30min Написать кастомное исключение
        raise ValueError(msg)
