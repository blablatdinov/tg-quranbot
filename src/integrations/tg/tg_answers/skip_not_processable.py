# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.update import Update
from exceptions.internal_exceptions import NotProcessableUpdateError
from integrations.tg.tg_answers.tg_answer import TgAnswer


@final
@attrs.define(frozen=True)
class TgSkipNotProcessable(TgAnswer):
    """Обработка и пропуск ответа, возбудившего NotProcessableUpdateError."""

    _answer: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            return await self._answer.build(update)
        except NotProcessableUpdateError:
            return []
