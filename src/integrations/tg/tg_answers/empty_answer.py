# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.stringable import SupportsStr
from app_types.update import Update
from integrations.tg.tg_answers.tg_answer import TgAnswer


@final
@attrs.define(frozen=True, repr=False)
class TgEmptyAnswer(TgAnswer, SupportsStr):
    """Пустой ответ."""

    _token: str

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Создать ответ с токеном.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [httpx.Request('GET', httpx.URL('https://api.telegram.org/bot{0}/'.format(self._token)))]

    @override
    def __str__(self) -> str:
        """Приведение к строке.

        :return: str
        """
        return 'TgEmptyAnswer(token=...)'
