# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from app_types.update import Update
from integrations.tg.callback_query import CallbackQueryData
from services.intable_regex import IntableRegex
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
        return cls(str(CallbackQueryData(update)))  # noqa: PEO102

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
