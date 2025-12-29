# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.fk_update import FkUpdate
from app_types.update import Update
from exceptions.content_exceptions import UserHasNotSearchQueryError
from integrations.tg.tg_answers import TgAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer
from srv.ayats.user_has_not_search_query_safe_answer import UserHasNotSearchQuerySafeAnswer


@final
@attrs.define(frozen=True)
class SeAnswer(TgAnswer):

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        raise UserHasNotSearchQueryError


async def test():
    got = await UserHasNotSearchQuerySafeAnswer(
        SeAnswer(),
        FkAnswer(),
    ).build(FkUpdate.empty_ctor())

    assert got[0].url == 'https://some.domain'
