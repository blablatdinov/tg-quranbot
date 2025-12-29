# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.update import Update
from integrations.tg.exceptions.update_parse_exceptions import CoordinatesNotFoundError
from integrations.tg.tg_answers.tg_answer import TgAnswer
from integrations.tg.tg_message_coordinates import TgMessageCoordinates


@final
@attrs.define(frozen=True)
class TgLocationAnswer(TgAnswer):
    """Ответ на присланную геопозицию."""

    _answer: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            TgMessageCoordinates(update).latitude()
        except CoordinatesNotFoundError:
            return []
        return await self._answer.build(update)
