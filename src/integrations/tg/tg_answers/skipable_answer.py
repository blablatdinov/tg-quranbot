# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer


@final
@attrs.define(frozen=True)
class SkipableAnswer(TgAnswer):
    """Декоратор для пропуска сообщения."""

    _skip: bool
    _origin: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        if self._skip:
            return []
        return await self._origin.build(update)
