# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

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
