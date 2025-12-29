# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.update import Update
from integrations.tg.tg_answers import TgAnswerToSender, TgHtmlParseAnswer, TgMessageAnswer
from integrations.tg.tg_answers.tg_answer import TgAnswer


@final
@attrs.define(frozen=True)
class TgHtmlMessageAnswerToSender(TgAnswer):  # noqa: PEO300
    """Ответ пользователю, от которого пришло сообщение."""

    _origin: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        return await TgAnswerToSender(
            TgHtmlParseAnswer(
                TgMessageAnswer(self._origin),
            ),
        ).build(update)
