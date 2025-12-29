# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.update import Update
from exceptions.internal_exceptions import UserNotFoundError
from integrations.tg.tg_answers.tg_answer import TgAnswer
from srv.users.new_user import NewUser


@final
@attrs.define(frozen=True)
class UserNotRegisteredSafeAnswer(TgAnswer):
    """Декоратор для обработки ошибки с незарегистрированным пользователем."""

    _new_user: NewUser
    _origin: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Обработка запроса.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except UserNotFoundError:
            await self._new_user.create()
        return await self._origin.build(update)
