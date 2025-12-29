# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer, TgTextAnswer
from srv.prayers.city import City
from srv.prayers.updated_user_city import UpdatedUserCity


@final
@attrs.define(frozen=True)
class ChangeCityAnswer(TgAnswer):
    """Ответ со сменой города."""

    _origin: TgAnswer
    _user_city: UpdatedUserCity
    _city: City

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        await self._user_city.update()
        return await TgTextAnswer.str_ctor(
            self._origin,
            'Вам будет приходить время намаза для города {0}'.format(await self._city.name()),
        ).build(update)
