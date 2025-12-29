# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from databases import Database

from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.message_text import MessageText
from integrations.tg.tg_answers import TgAnswer
from srv.ayats.ayat_answer import AyatAnswer
from srv.ayats.ayat_answer_keyboard import AyatAnswerKeyboard
from srv.ayats.ayat_callback_template_enum import AyatCallbackTemplateEnum
from srv.ayats.pg_ayat import PgAyat
from srv.ayats.pg_neighbor_ayats import PgNeighborAyats
from srv.ayats.text_len_shorten_ayat import TextLenSafeAyat


@final
@attrs.define(frozen=True)
class AyatBySuraAyatNumAnswer(TgAnswer):
    """Ответ на поиск аята по номеру суры, аята."""

    _debug_mode: SupportsBool
    _empty_answer: TgAnswer
    _file_answer: TgAnswer
    _pgsql: Database

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        result_ayat = TextLenSafeAyat(PgAyat.by_sura_ayat_num(MessageText(update), self._pgsql))
        return await AyatAnswer(
            self._debug_mode,
            self._empty_answer,
            result_ayat,
            AyatAnswerKeyboard(
                result_ayat,
                PgNeighborAyats(self._pgsql, await result_ayat.identifier().ayat_id()),
                AyatCallbackTemplateEnum.get_ayat,
                self._pgsql,
            ),
        ).build(update)
