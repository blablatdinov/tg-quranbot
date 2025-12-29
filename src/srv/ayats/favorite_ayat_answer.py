# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from databases import Database

from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer
from integrations.tg.tg_chat_id import TgChatId
from srv.ayats.ayat_answer import AyatAnswer
from srv.ayats.ayat_answer_keyboard import AyatAnswerKeyboard
from srv.ayats.ayat_callback_template_enum import AyatCallbackTemplateEnum
from srv.ayats.favorite_ayats import FavoriteAyats
from srv.ayats.favorite_neighbor_ayats import FavoriteNeighborAyats
from srv.ayats.favorites.user_favorite_ayats import UserFavoriteAyats


@final
@attrs.define(frozen=True)
class FavoriteAyatAnswer(TgAnswer):
    """Ответ с избранными аятами."""

    _debug_mode: SupportsBool
    _empty_answer: TgAnswer
    _pgsql: Database

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        result_ayat = (
            await FavoriteAyats(
                TgChatId(update),
                self._pgsql,
            ).to_list()
        )[0]
        return await AyatAnswer(
            self._debug_mode,
            self._empty_answer,
            result_ayat,
            AyatAnswerKeyboard(
                result_ayat,
                FavoriteNeighborAyats(
                    await result_ayat.identifier().ayat_id(), UserFavoriteAyats(self._pgsql, TgChatId(update)),
                ),
                AyatCallbackTemplateEnum.get_favorite_ayat,
                self._pgsql,
            ),
        ).build(update)
