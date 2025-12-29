# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer


@final
@attrs.define(frozen=True)
class FavoriteAyatEmptySafeAnswer(TgAnswer):
    """Обработка ошибок с пустыми избранными."""

    _origin: TgAnswer
    _error_answer: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except IndexError:  # @todo #360:30min
            return await self._error_answer.build(update)
