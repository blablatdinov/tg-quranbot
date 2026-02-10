# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.fk_update import FkUpdate
from app_types.update import Update
from exceptions.content_exceptions import CityNotSupportedError
from integrations.tg.tg_answers import TgAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer
from srv.prayers.city_not_supported_answer import CityNotSupportedAnswer


@final
@attrs.define(frozen=True)
class _Answer(TgAnswer):

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        raise CityNotSupportedError


async def test_city_not_supported():
    got = await CityNotSupportedAnswer(_Answer(), FkAnswer()).build(FkUpdate.empty_ctor())

    assert got[0].url.params['text'] == 'Этот город не поддерживается'
