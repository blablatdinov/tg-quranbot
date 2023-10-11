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
from typing import final

import attrs
import pytz
from pyeo import elegant

from app_types.date_time import DateTimeInterface
from app_types.stringable import SupportsStr


@final
@attrs.define(frozen=True)
@elegant
class PrayerDate(DateTimeInterface):
    """Дата намаза."""

    _message: SupportsStr

    def datetime(self) -> datetime.datetime:
        """Дата/время.

        :return: datetime.datetime
        :raises ValueError: time not parsed
        """
        date = str(self._message).split(' ')[-1]
        if date == 'намаза':
            return datetime.datetime.now(pytz.timezone('Europe/Moscow'))
        formats = ('%d.%m.%Y', '%d-%m-%Y')  # noqa: WPS323 not string formatting
        for fmt in formats:
            with suppress(ValueError):
                return datetime.datetime.strptime(date, fmt)
        raise ValueError("time data '{0}' does not match formats {1}".format(
            date, formats,
        ))
