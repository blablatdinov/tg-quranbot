# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from app_types.fk_log_sink import FkLogSink
from app_types.fk_update import FkUpdate
from exceptions.internal_exceptions import NotProcessableUpdateError
from integrations.tg.tg_answers import TgAnswerFork
from integrations.tg.tg_answers.fk_answer import FkAnswer


async def test():
    got = await TgAnswerFork.ctor(
        FkLogSink(),
        FkAnswer(),
    ).build(FkUpdate.empty_ctor())

    assert got[0].url == 'https://some.domain'
    assert len(got) == 1


async def test_not_processable():
    with pytest.raises(NotProcessableUpdateError):
        await TgAnswerFork.ctor(
            FkLogSink(),
        ).build(FkUpdate.empty_ctor())
