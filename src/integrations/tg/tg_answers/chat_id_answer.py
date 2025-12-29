# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from furl import furl

from app_types.update import Update
from integrations.tg.fk_chat_id import ChatId
from integrations.tg.tg_answers.tg_answer import TgAnswer


@final
@attrs.define(frozen=True)
class TgChatIdAnswer(TgAnswer):
    """Ответ пользователю на конкретный идентификатор чата."""

    _origin: TgAnswer
    _chat_id: ChatId

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                request.method,
                furl(request.url).add({'chat_id': int(self._chat_id)}).url,
                stream=request.stream,
                headers=request.headers,
            )
            for request in await self._origin.build(update)
        ]
