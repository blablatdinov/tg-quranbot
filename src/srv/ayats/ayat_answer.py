# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.keyboard import Keyboard
from integrations.tg.tg_answers import (
    TgAnswer,
    TgAnswerList,
    TgAnswerMarkup,
    TgAnswerToSender,
    TgAudioAnswer,
    TgLinkPreviewOptions,
    TgTextAnswer,
)
from integrations.tg.tg_answers.message_answer_to_sender import TgHtmlMessageAnswerToSender
from srv.ayats.ayat import Ayat
from srv.files.file_answer import FileAnswer
from srv.files.file_id_answer import TelegramFileIdAnswer


@final
@attrs.define(frozen=True)
class AyatAnswer(TgAnswer):
    """Ответ с аятом."""

    _debug_mode: SupportsBool
    _empty_answer: TgAnswer
    _ayat: Ayat
    _ayat_answer_keyboard: Keyboard

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return await TgAnswerList.ctor(
            TgLinkPreviewOptions(
                TgAnswerMarkup(
                    TgTextAnswer(
                        TgHtmlMessageAnswerToSender(self._empty_answer),
                        self._ayat,
                    ),
                    self._ayat_answer_keyboard,
                ),
                disabled=True,
            ),
            FileAnswer(
                TelegramFileIdAnswer(
                    TgAnswerToSender(TgAudioAnswer(self._empty_answer)),
                    await self._ayat.audio(),
                ),
                TgTextAnswer.str_ctor(
                    TgHtmlMessageAnswerToSender(self._empty_answer),
                    await (await self._ayat.audio()).file_link(),
                ),
                self._debug_mode,
            ),
        ).build(update)
