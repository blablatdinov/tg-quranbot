# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from app_types.update import Update
from integrations.tg.keyboard import Keyboard


@final
@attrs.define(frozen=True)
class FkKeyboard(Keyboard):
    """Фейковая клавиатура."""

    _json_keyboard: str

    @classmethod
    def empty_ctor(cls) -> Keyboard:
        """Empty ctor.

        :return: Keyboard
        """
        return cls('{}')

    @override
    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        :return: str
        """
        return self._json_keyboard
