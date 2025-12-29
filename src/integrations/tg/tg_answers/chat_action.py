# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from furl import furl

from app_types.update import Update
from integrations.tg.tg_answers.tg_answer import TgAnswer


@final
@attrs.define(frozen=True)
class TgChatAction(TgAnswer):
    """Запрос на API телеграма с действием.

    Используется для проверки статуса пользователя.
    """

    _origin: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Формирование запросов.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                request.method,
                (furl(request.url) / 'sendChatAction').url,
                headers=request.headers,
            )
            for request in await self._origin.build(update)
        ]
