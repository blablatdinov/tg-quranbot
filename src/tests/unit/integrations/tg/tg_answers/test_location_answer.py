# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from app_types.fk_update import FkUpdate
from integrations.tg.tg_answers.fk_answer import FkAnswer
from integrations.tg.tg_answers.location_answer import TgLocationAnswer


async def test():
    got = await TgLocationAnswer(FkAnswer()).build(FkUpdate(
        '{"latitude": 0, "longitude": 0}',
    ))

    assert got[0].url == 'https://some.domain'


async def test_not_match():
    got = await TgLocationAnswer(FkAnswer()).build(FkUpdate.empty_ctor())

    assert got == []
