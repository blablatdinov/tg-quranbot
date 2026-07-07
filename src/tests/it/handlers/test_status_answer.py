# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from app_types.fk_update import FkUpdate
from handlers.status_answer import StatusAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer


async def test(pgsql, fake_redis):
    got = await StatusAnswer(FkAnswer(), pgsql, fake_redis).build(
        FkUpdate('{"chat":{"id":1}}'),
    )
    answer_text = got[0].url.params['text']

    assert 'DB' in answer_text
    assert 'Redis' in answer_text
