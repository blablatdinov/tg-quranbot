# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from collections.abc import Iterable
from typing import final, override

import attrs
import httpx

from app_types.update import Update
from integrations.tg.tg_answers.tg_answer import TgAnswer


@final
@attrs.define(frozen=True)
class TgAnswerList(TgAnswer):
    """Список ответов пользователю."""

    _answers: Iterable[TgAnswer]

    @classmethod
    def ctor(cls, *answers: TgAnswer) -> TgAnswer:
        """Конструктор класса.

        :param answers: TgAnswerInterface
        :return: TgAnswer
        """
        return cls(
            answers,
        )

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        rebuilded_requests = []
        for answer in self._answers:
            answer_requests = await answer.build(update)
            rebuilded_requests += answer_requests
        return rebuilded_requests
