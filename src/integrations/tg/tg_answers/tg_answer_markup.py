# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from furl import furl

from app_types.update import Update
from integrations.tg.keyboard import Keyboard
from integrations.tg.tg_answers.tg_answer import TgAnswer


@final
@attrs.define(frozen=True)
class TgAnswerMarkup(TgAnswer):
    """Ответ с клавиатурой."""

    _origin: TgAnswer
    _keyboard: Keyboard

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ для пользователя.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                request.method,
                furl(request.url).add(
                    {'reply_markup': await self._keyboard.generate(update)},
                ).url,
                stream=request.stream,
                headers=request.headers,
            )
            for request in await self._origin.build(update)
        ]
