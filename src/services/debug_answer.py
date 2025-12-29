# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.update import Update
from integrations.tg.tg_answers.answer_to_sender import TgAnswerToSender
from integrations.tg.tg_answers.message_answer import TgMessageAnswer
from integrations.tg.tg_answers.text_answer import TgTextAnswer
from integrations.tg.tg_answers.tg_answer import TgAnswer
from integrations.tg.update_id import UpdateId


@final
@attrs.define(frozen=True)
class DebugAnswer(TgAnswer):
    """Ответ для отладки."""

    _origin: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :returns: list[httpx.Request]
        """
        return await TgTextAnswer.str_ctor(
            TgAnswerToSender(
                TgMessageAnswer(self._origin),
            ),
            'DEBUG. Update <{0}>'.format(int(UpdateId(update))),
        ).build(update)
