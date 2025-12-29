# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.update import Update
from integrations.tg.exceptions.update_parse_exceptions import MessageTextNotFoundError
from integrations.tg.tg_answers import TgAnswer


@final
@attrs.define(frozen=True)
class MessageNotFoundSafeAnswer(TgAnswer):
    """MessageNotFoundSafeAnswer."""

    _origin: TgAnswer
    _new_message_answer: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except MessageTextNotFoundError:
            return await self._new_message_answer.build(update)
