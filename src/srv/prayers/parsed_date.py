# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
