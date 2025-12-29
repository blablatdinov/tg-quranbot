# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from furl import furl

from app_types.update import Update
from integrations.tg.tg_answers.tg_answer import TgAnswer
from integrations.tg.tg_chat_id import TgChatId


@final
@attrs.define(frozen=True)
class TgAnswerToSender(TgAnswer):  # noqa: PEO300
    """Ответ пользователю, от которого пришло сообщение."""

    _origin: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                request.method,
                furl(request.url).add({'chat_id': int(TgChatId(update))}).url,
            )
            for request in await self._origin.build(update)
        ]
