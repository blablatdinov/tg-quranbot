# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.update import Update
from exceptions.user import UserAlreadyActiveError
from integrations.tg.tg_answers import TgAnswer, TgTextAnswer


@final
@attrs.define(frozen=True)
class UserAlreadyActiveSafeAnswer(TgAnswer):
    """Ответ для случаев когда пользователь уже активен."""

    _origin: TgAnswer
    _sender_answer: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except UserAlreadyActiveError:
            return await TgTextAnswer.str_ctor(
                self._sender_answer,
                'Вы уже зарегистрированы!',
            ).build(update)
