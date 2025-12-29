# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from databases import Database

from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer, TgAnswerMarkup, TgTextAnswer
from integrations.tg.tg_chat_id import TgChatId
from srv.ayats.ayat import Ayat
from srv.ayats.ayat_callback_template_enum import AyatCallbackTemplateEnum
from srv.ayats.ayat_favorite_keyboard_button import AyatFavoriteKeyboardButton
from srv.ayats.favorites.ayat_is_favor import AyatIsFavor
from srv.ayats.neighbor_ayat_keyboard import NeighborAyatKeyboard
from srv.ayats.pg_neighbor_ayats import PgNeighborAyats


@final
@attrs.define(frozen=True)
class AyatByIdMessageAnswer(TgAnswer):
    """Текстовый ответ на поиск аята."""

    _result_ayat: Ayat
    _message_answer: TgAnswer
    _pgsql: Database

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return await TgAnswerMarkup(
            TgTextAnswer(
                self._message_answer,
                self._result_ayat,
            ),
            AyatFavoriteKeyboardButton(
                NeighborAyatKeyboard(
                    PgNeighborAyats(self._pgsql, await self._result_ayat.identifier().ayat_id()),
                    AyatCallbackTemplateEnum.get_ayat,
                ),
                AyatIsFavor(
                    self._result_ayat,
                    TgChatId(update),
                    self._pgsql,
                ),
                self._result_ayat,
            ),
        ).build(update)
