# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import ujson

from app_types.update import Update
from integrations.tg.keyboard import Keyboard
from srv.ayats.ayat_callback_template_enum import AyatCallbackTemplateEnum
from srv.ayats.neighbor_ayats import NeighborAyats
from srv.ayats.neighbor_ayats_btns import NeighborAyatsBtns


@final
@attrs.define(frozen=True)
class NeighborAyatKeyboard(Keyboard):
    """Клавиатура с соседними аятами."""

    _ayats_neighbors: NeighborAyats
    _callback_template: AyatCallbackTemplateEnum

    @override
    async def generate(self, update: Update) -> str:
        """Генерация клавиатуры.

        :param update: Update
        :return: str
        """
        buttons = []
        btns = NeighborAyatsBtns(self._ayats_neighbors, self._callback_template)
        left_button = await btns.left()
        if left_button:
            buttons.append(left_button)
        buttons.append({
            'text': await self._ayats_neighbors.page(),
            'callback_data': 'fake',
        })
        right_button = await btns.right()
        if right_button:
            buttons.append(right_button)
        return ujson.dumps({
            'inline_keyboard': [buttons],
        })
