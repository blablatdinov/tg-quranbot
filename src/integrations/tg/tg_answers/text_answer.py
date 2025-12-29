# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from furl import furl

from app_types.async_supports_str import AsyncSupportsStr
from app_types.fk_async_str import FkAsyncStr
from app_types.update import Update
from integrations.tg.tg_answers.tg_answer import TgAnswer


@final
@attrs.define(frozen=True)
class TgTextAnswer(TgAnswer):
    """Ответ пользователю с текстом."""

    _origin: TgAnswer
    _text: AsyncSupportsStr

    @classmethod
    def str_ctor(cls, origin: TgAnswer, text: str) -> TgAnswer:
        """Конструктор для строки.

        :param origin: TgAnswer
        :param text: str
        :return: TgAnswer
        """
        return cls(
            origin, FkAsyncStr(text),
        )

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                request.method,
                furl(request.url).add({'text': await self._text.to_str()}).url,
            )
            for request in await self._origin.build(update)
        ]
