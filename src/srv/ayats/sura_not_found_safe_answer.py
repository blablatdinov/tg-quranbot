# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.update import Update
from exceptions.content_exceptions import SuraNotFoundError
from integrations.tg.tg_answers import TgAnswer, TgTextAnswer


@final
@attrs.define(frozen=True)
class SuraNotFoundSafeAnswer(TgAnswer):
    """Объект обрабатывающий ошибку с не найденной сурой."""

    _origin: TgAnswer
    _error_answer: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :returns: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except SuraNotFoundError:
            return await TgTextAnswer.str_ctor(
                self._error_answer,
                'Сура не найдена',
            ).build(update)
