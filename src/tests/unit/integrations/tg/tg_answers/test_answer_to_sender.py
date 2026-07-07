# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from app_types.fk_update import FkUpdate
from integrations.tg.tg_answers import TgAnswerToSender
from integrations.tg.tg_answers.fk_answer import FkAnswer


async def test():
    got = await TgAnswerToSender(FkAnswer()).build(FkUpdate('{"chat":{"id":123}}'))

    assert got[0].url == 'https://some.domain?chat_id=123'
