# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
