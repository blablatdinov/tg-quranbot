# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import ujson

from app_types.update import Update
from integrations.tg.keyboard import Keyboard


@final
@attrs.define(frozen=True)
class ResizedKeyboard(Keyboard):
    """Сжатая в высоту клавиатура."""

    _origin: Keyboard

    @override
    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        :return: str
        """
        origin_keyboard = await self._origin.generate(update)
        keyboard_as_dict = ujson.loads(origin_keyboard)
        keyboard_as_dict['resize_keyboard'] = True
        return ujson.dumps(keyboard_as_dict)
