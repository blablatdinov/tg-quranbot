# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from app_types.fk_update import FkUpdate
from integrations.tg.tg_answers import TgAnswerList
from integrations.tg.tg_answers.fk_answer import FkAnswer


async def test():
    got = await TgAnswerList.ctor(
        FkAnswer(),
        FkAnswer(),
    ).build(FkUpdate.empty_ctor())

    assert len(got) == 2
    assert [request.url for request in got] == ['https://some.domain', 'https://some.domain']
