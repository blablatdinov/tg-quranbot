"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
from typing import final

import attrs
import httpx
from pyeo import elegant

from app_types.intable import ThroughAsyncIntable
from app_types.update import Update
from db.connection import database
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.tg_answers import TgAnswer, TgAnswerList, TgTextAnswer
from services.regular_expression import IntableRegularExpression
from srv.ayats.ayat_by_id_message_answer import AyatByIdMessageAnswer
from srv.ayats.pg_ayat import PgAyat
from srv.files.file_answer import FileAnswer
from srv.files.file_id_answer import TelegramFileIdAnswer


@final
@attrs.define(frozen=True)
@elegant
class AyatByIdAnswer(TgAnswer):
    """Ответ на аят по идентификатору."""

    _debug_mode: bool
    _message_answer: TgAnswer
    _file_answer: TgAnswer

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        result_ayat = PgAyat(
            ThroughAsyncIntable(
                int(IntableRegularExpression(
                    str(CallbackQueryData(update)),
                )),
            ),
            database,
        )
        return await TgAnswerList(
            AyatByIdMessageAnswer(
                result_ayat, self._message_answer,
            ),
            FileAnswer(
                self._debug_mode,
                TelegramFileIdAnswer(
                    self._file_answer,
                    await result_ayat.tg_file_id(),
                ),
                TgTextAnswer(
                    self._message_answer,
                    await result_ayat.file_link(),
                ),
            ),
        ).build(update)