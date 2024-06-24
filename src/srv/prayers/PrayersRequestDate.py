from app_types.update import Update
from integrations.tg.message_text import MessageText
from srv.prayers.prayer_date import PrayerDate


import attrs
import pytz
from pyeo import elegant


import datetime
from contextlib import suppress
from typing import final, override


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
                return datetime.datetime.strptime(date, fmt).astimezone(
                    pytz.timezone('Europe/Moscow'),
                ).date()
        msg = "time data '{0}' does not match formats {1}".format(date, formats)
        raise ValueError(msg)