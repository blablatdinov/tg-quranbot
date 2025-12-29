# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from app_types.fk_update import FkUpdate
from exceptions.content_exceptions import SuraNotFoundError
from integrations.tg.tg_answers import TgAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer
from srv.ayats.sura_not_found_safe_answer import SuraNotFoundSafeAnswer


@final
@attrs.define(frozen=True)
class SuraNotFoundAnswer(TgAnswer):

    @override
    async def build(self, update):
        raise SuraNotFoundError


async def test_normal_flow():
    got = await SuraNotFoundSafeAnswer(
        FkAnswer('https://normal.flow'),
        FkAnswer('https://error.flow'),
    ).build(FkUpdate.empty_ctor())

    assert got[0].url == 'https://normal.flow'


async def test_error_flow():
    got = await SuraNotFoundSafeAnswer(
        SuraNotFoundAnswer(),
        FkAnswer('https://error.flow'),
    ).build(FkUpdate.empty_ctor())

    assert 'error.flow' in str(got[0].url)
