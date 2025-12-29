# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from typing import final, override

import attrs
import pytz

from app_types.update import Update
from integrations.tg.callback_query import CallbackQueryData
from srv.prayers.prayer_date import PrayerDate


@final
@attrs.define(frozen=True)
class PaginationPerDayDate(PrayerDate):
    """Дата намаза."""

    @override
    async def parse(self, update: Update) -> datetime.date:
        """Парсинг даты из информации о нажатии на кнопку.

        :param update: Update
        :return: datetime.date
        """
        return datetime.datetime.strptime(
            str(CallbackQueryData(update)).split('(')[1][:-1],
            '%Y-%m-%d',
        ).astimezone(pytz.timezone('Europe/Moscow')).date()
