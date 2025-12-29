# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import ujson

from app_types.update import Update
from integrations.tg.keyboard import Keyboard
from srv.prayers.prayer_names import PrayerNames


@final
@attrs.define(frozen=True)
class SkippedPrayersKeyboard(Keyboard):
    """Клавиатура для пропущеных намазов."""

    @override
    async def generate(self, update: Update) -> str:
        """Генерация клавиатуры.

        :param update: Update
        :return: str
        """
        return ujson.dumps({
            'inline_keyboard': [
                [{
                    'text': '{0}: (-1)'.format(field.value[1]),
                    'callback_data': 'decr({0})'.format(field.name),
                }]
                for field in PrayerNames.fields_without_sunrise()
            ],
        })
