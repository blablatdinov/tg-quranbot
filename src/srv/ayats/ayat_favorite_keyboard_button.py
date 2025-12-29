# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import ujson

from app_types.async_supports_bool import AsyncSupportsBool
from app_types.update import Update
from integrations.tg.keyboard import Keyboard
from srv.ayats.ayat import Ayat


@final
@attrs.define(frozen=True)
class AyatFavoriteKeyboardButton(Keyboard):
    """Кнопка с добавлением аята в избранные."""

    _origin: Keyboard
    _is_favor: AsyncSupportsBool
    _ayat: Ayat

    @override
    async def generate(self, update: Update) -> str:
        """Генерация клавиатуры.

        :param update: Update
        :return: str
        """
        keyboard = ujson.loads(await self._origin.generate(update))
        is_favor = await self._is_favor.to_bool()
        keyboard['inline_keyboard'].append([{
            'text': 'Удалить из избранного' if is_favor else 'Добавить в избранное',
            'callback_data': ('removeFromFavor({0})' if is_favor else 'addToFavor({0})').format(
                await self._ayat.identifier().ayat_id(),
            ),
        }])
        return ujson.dumps(keyboard)
