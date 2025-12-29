# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer


@final
@attrs.define(frozen=True)
class TypingAction(TgAnswer):
    """Действие с печатью."""

    _origin: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                method=request.method, url=request.url.copy_add_param('action', 'typing'), headers=request.headers,
            )
            for request in await self._origin.build(update)
        ]
