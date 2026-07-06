# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT


from typing import final, override

import attrs

from app_types.update import Update
from integrations.tg.keyboard import Keyboard


@final
@attrs.define(frozen=True)
class DefaultKeyboard(Keyboard):
    """Класс клавиатуры по умолчанию."""

    @override
    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        :return: str
        """
        return '{"keyboard":[["🎧 Подкасты"],["🕋 Время намаза","🏘️ Поменять город"],["🌟 Избранное","🔍 Найти аят"]]}'
