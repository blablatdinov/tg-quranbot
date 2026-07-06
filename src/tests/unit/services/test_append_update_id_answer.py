# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from app_types.fk_update import FkUpdate
from integrations.tg.tg_answers import TgMessageAnswer, TgTextAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer
from services.append_debug_info_answer import AppendDebugInfoAnswer
from services.update_id_debug_param import UpdateIdDebugParam


async def test():
    got = await AppendDebugInfoAnswer.ctor(
        TgTextAnswer.str_ctor(
            TgMessageAnswer(
                FkAnswer(),
            ),
            'text',
        ),
        UpdateIdDebugParam(),
        debug_mode=True,
    ).build(FkUpdate('{"update_id": 1}'))

    assert got[0].url.params['text'] == '\n\n'.join([
        'text',
        '!----- DEBUG INFO -----!',
        'Update id: 1',
        '!----- END DEBUG INFO -----!',
    ])
