from app_types.update import Update
from services.DebugParam import DebugParam


import pytz


import datetime
from typing import final, override


@final
@elegant
class TimeDebugParam(DebugParam):
    """Отладочная информация с временем."""

    @override
    async def debug_value(self, update: Update) -> str:
        """Время.

        :param update: Update
        :return: str
        """
        return 'Time: {0}'.format(datetime.datetime.now(pytz.timezone('Europe/Moscow')))