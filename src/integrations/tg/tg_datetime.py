import datetime
import re

import pytz

from app_types.date_time import DateTimeIterface
from app_types.stringable import Stringable
from exceptions.base_exception import InternalBotError


class TgDateTime(DateTimeIterface):
    """Время сообщения."""

    def __init__(self, update: Stringable):
        """Конструктор класса.

        :param update: Stringable
        """
        self._update = update

    def datetime(self) -> datetime.datetime:
        """Дата/время.

        :return: datetime.datetime
        :raises InternalBotError: если время не найдено
        """
        regex_result = re.search(r'date"(:|: )(\d+)', str(self._update))
        if not regex_result:
            raise InternalBotError
        return datetime.datetime.fromtimestamp(
            int(regex_result.group(2)),
            tz=pytz.timezone('UTC'),
        )
