# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from databases import Database

from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.tg_answers import TgAnswer, TgAnswerList, TgAnswerToSender, TgAudioAnswer, TgTextAnswer
from integrations.tg.tg_answers.message_answer_to_sender import TgHtmlMessageAnswerToSender
from srv.ayats.ayat_by_id_message_answer import AyatByIdMessageAnswer
from srv.ayats.pg_ayat import PgAyat
from srv.ayats.text_len_shorten_ayat import TextLenSafeAyat
from srv.files.file_answer import FileAnswer
from srv.files.file_id_answer import TelegramFileIdAnswer


@final
@attrs.define(frozen=True)
class AyatByIdAnswer(TgAnswer):
    """Ответ на аят по идентификатору."""

    _debug_mode: SupportsBool
    _empty_answer: TgAnswer
    _pgsql: Database

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        result_ayat = TextLenSafeAyat(PgAyat.from_callback_query(CallbackQueryData(update), self._pgsql))
        return await TgAnswerList.ctor(
            AyatByIdMessageAnswer(
                result_ayat, TgHtmlMessageAnswerToSender(self._empty_answer), self._pgsql,
            ),
            FileAnswer(
                TelegramFileIdAnswer(
                    TgAnswerToSender(TgAudioAnswer(self._empty_answer)),
                    await result_ayat.audio(),
                ),
                TgTextAnswer.str_ctor(
                    TgHtmlMessageAnswerToSender(self._empty_answer),
                    await (await result_ayat.audio()).file_link(),
                ),
                self._debug_mode,
            ),
        ).build(update)
