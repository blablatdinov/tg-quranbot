# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import httpx

from app_types.fk_update import FkUpdate
from app_types.update import Update
from exceptions.internal_exceptions import UserNotFoundError
from integrations.tg.tg_answers import TgAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer
from srv.prayers.user_not_registered_safe_answer import UserNotRegisteredSafeAnswer
from srv.users.fk_new_user import FkNewUser


@final
class UserNotFoundAnswer(TgAnswer):  # noqa: PEO200. Test class

    def __init__(self, origin: TgAnswer):
        self._origin = origin
        self._counter = 0

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        if self._counter == 0:
            self._counter += 1
            raise UserNotFoundError
        return await self._origin.build(update)


async def test():
    got = await UserNotRegisteredSafeAnswer(
        FkNewUser(),
        FkAnswer(),
    ).build(FkUpdate.empty_ctor())

    assert got[0].url == 'https://some.domain'


async def test_user_not_found():
    got = await UserNotRegisteredSafeAnswer(
        FkNewUser(),
        UserNotFoundAnswer(FkAnswer()),
    ).build(FkUpdate.empty_ctor())

    assert got[0].url == 'https://some.domain'
