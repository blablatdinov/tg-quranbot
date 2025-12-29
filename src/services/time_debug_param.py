# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from typing import final, override

import attrs
import pytz

from app_types.update import Update
from services.debug_param import DebugParam


@final
@attrs.define(frozen=True)
class TimeDebugParam(DebugParam):
    """Отладочная информация с временем."""

    @override
    async def debug_value(self, update: Update) -> str:
        """Время.

        :param update: Update
        :return: str
        """
        return 'Time: {0}'.format(datetime.datetime.now(pytz.timezone('Europe/Moscow')))
