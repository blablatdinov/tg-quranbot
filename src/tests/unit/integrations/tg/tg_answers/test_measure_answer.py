# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import re

from app_types.fk_update import FkUpdate
from integrations.tg.tg_answers import TgMeasureAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer


async def test(fk_logger):
    got = await TgMeasureAnswer(FkAnswer(), fk_logger).build(FkUpdate('{"update_id":1}'))

    assert got[0].url == 'https://some.domain'
    assert re.match(
        r'INFO Update <1> process time: \d{1,3}.\d{2} ms',
        fk_logger.stack[1],
    )
