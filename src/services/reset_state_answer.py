# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer
from srv.users.user_state import UserState
from srv.users.user_step import UserStep


@final
@attrs.define(frozen=True)
class ResetStateAnswer(TgAnswer):
    """Декоратор для обнуления состояния пользователя."""

    _origin: TgAnswer
    _user_state: UserState

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        requests = await self._origin.build(update)
        await self._user_state.change_step(UserStep.nothing)
        return requests
