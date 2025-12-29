# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from typing import final, override

import attrs
import pytz

from app_types.update import Update
from integrations.tg.message_text import MessageText
from srv.prayers.prayer_date import PrayerDate


@final
@attrs.define(frozen=True)
class PrayersMarkAsDate(PrayerDate):
    """Дата намаза при редактировании."""

    @override
    async def parse(self, update: Update) -> datetime.date:
        """Парсинг из текста сообщения.

        :param update: Update
        :return: datetime.date
        """
        msg_first_line = str(MessageText(update)).split('\n', maxsplit=1)[0]
        date = msg_first_line.split(' ')[-1][1:-1]
        return (
            datetime.datetime
            .strptime(date, '%d.%m.%Y')  # noqa: WPS323 not string formatting
            .astimezone(pytz.timezone('Europe/Moscow'))
            .date()
        )
