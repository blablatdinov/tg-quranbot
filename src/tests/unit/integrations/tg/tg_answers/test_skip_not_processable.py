# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.fk_update import FkUpdate
from app_types.update import Update
from exceptions.internal_exceptions import NotProcessableUpdateError
from integrations.tg.tg_answers import TgAnswer
from integrations.tg.tg_answers.skip_not_processable import TgSkipNotProcessable


@final
@attrs.define(frozen=True)
class _NotProcessableAnswer(TgAnswer):

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        raise NotProcessableUpdateError


async def test():
    got = await TgSkipNotProcessable(_NotProcessableAnswer()).build(FkUpdate.empty_ctor())

    assert got == []
