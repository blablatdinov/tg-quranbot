# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from app_types.fk_update import FkUpdate
from exceptions.content_exceptions import AyatNotFoundError
from integrations.tg.tg_answers import TgAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer
from srv.ayats.ayat_not_found_safe_answer import AyatNotFoundSafeAnswer


@final
@attrs.define(frozen=True)
class AyatNotFoundAnswer(TgAnswer):

    @override
    async def build(self, update):
        raise AyatNotFoundError


async def test_normal_flow():
    got = await AyatNotFoundSafeAnswer(
        FkAnswer('https://normal.flow'),
        FkAnswer('https://error.flow'),
    ).build(FkUpdate.empty_ctor())

    assert got[0].url == 'https://normal.flow'


async def test_error_flow():
    got = await AyatNotFoundSafeAnswer(
        AyatNotFoundAnswer(),
        FkAnswer('https://error.flow'),
    ).build(FkUpdate.empty_ctor())

    assert 'error.flow' in str(got[0].url)
