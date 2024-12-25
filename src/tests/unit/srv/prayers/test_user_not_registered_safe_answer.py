# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

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
