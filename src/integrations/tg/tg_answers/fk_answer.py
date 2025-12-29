# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.update import Update
from integrations.tg.tg_answers.tg_answer import TgAnswer


@final
@attrs.define(frozen=True)
class FkAnswer(TgAnswer):
    """Фейковый ответ."""

    _url: str | None = 'https://some.domain'

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        :raises ValueError: if self._url is None
        """
        if self._url is None:
            raise ValueError
        return [httpx.Request('GET', self._url)]
