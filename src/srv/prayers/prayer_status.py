# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

from typing import final, override

import attrs

from app_types.update import Update
from integrations.tg.callback_query import CallbackQueryData
from services.instable_regex import IntableRegex
from srv.prayers.prayers_stts import PrayerStts


@final
@attrs.define(frozen=True)
class PrayerStatus(PrayerStts):
    """Объект, рассчитывающий данные кнопки для изменения статуса прочитанности намаза."""

    _source: str

    @classmethod
    def update_ctor(cls, update: Update) -> PrayerStts:
        """Конструктор для update.

        :param update: Update
        :return: PrayerStatusInterface
        """
        return cls(str(CallbackQueryData(update)))

    @override
    def user_prayer_id(self) -> int:
        """Рассчитать идентификатор времени намаза пользователя.

        :return: int
        """
        return int(IntableRegex(self._source))

    @override
    def change_to(self) -> bool:
        """Рассчитать статус времени намаза пользователя.

        :return: bool
        """
        return 'not' not in self._source.split('(')[0]
