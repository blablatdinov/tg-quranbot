# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from app_types.fk_update import FkUpdate
from integrations.tg.fk_keyboard import FkKeyboard
from integrations.tg.tg_answers import TgAnswerMarkup
from integrations.tg.tg_answers.fk_answer import FkAnswer


async def test(unquote):
    got = await TgAnswerMarkup(
        FkAnswer(),
        FkKeyboard.empty_ctor(),
    ).build(FkUpdate.empty_ctor())

    assert unquote(str(got[0].url)) == 'https://some.domain?reply_markup={}'
