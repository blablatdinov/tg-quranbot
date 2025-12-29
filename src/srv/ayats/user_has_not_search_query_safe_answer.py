# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.update import Update
from exceptions.content_exceptions import UserHasNotSearchQueryError
from integrations.tg.tg_answers import TgAnswer


@final
@attrs.define(frozen=True)
class UserHasNotSearchQuerySafeAnswer(TgAnswer):
    """Обработка исключения с отсутствием запроса к поиску аятов."""

    _origin: TgAnswer
    _fail_answer: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except UserHasNotSearchQueryError:
            return await self._fail_answer.build(update)
