# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from databases import Database

from app_types.update import Update
from integrations.tg.keyboard import Keyboard
from integrations.tg.tg_chat_id import TgChatId
from srv.ayats.ayat import Ayat
from srv.ayats.ayat_callback_template_enum import AyatCallbackTemplateEnum
from srv.ayats.ayat_favorite_keyboard_button import AyatFavoriteKeyboardButton
from srv.ayats.favorites.ayat_is_favor import AyatIsFavor
from srv.ayats.neighbor_ayat_keyboard import NeighborAyatKeyboard
from srv.ayats.neighbor_ayats import NeighborAyats


@final
@attrs.define(frozen=True)
class AyatAnswerKeyboard(Keyboard):
    """Клавиатура аята."""

    _ayat: Ayat
    _neighbor_ayats: NeighborAyats
    _ayat_callback_template: AyatCallbackTemplateEnum
    _pgsql: Database

    @override
    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        :return: str
        """
        return await AyatFavoriteKeyboardButton(
            NeighborAyatKeyboard(self._neighbor_ayats, self._ayat_callback_template),
            AyatIsFavor(
                self._ayat,
                TgChatId(update),
                self._pgsql,
            ),
            self._ayat,
        ).generate(update)
