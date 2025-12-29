# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import ujson

from app_types.update import Update
from services.answers.resized_keyboard import Keyboard


@final
@attrs.define(frozen=True)
class SwitchInlineQueryKeyboard(Keyboard):
    """Переключение на инлайн поиск."""

    @override
    async def generate(self, update: Update) -> str:
        """Сборка клавиатуры.

        :param update: Update
        :return: str
        """
        return ujson.dumps({
            'inline_keyboard': [
                [{'text': 'Поиск города', 'switch_inline_query_current_chat': ''}],
            ],
        })
