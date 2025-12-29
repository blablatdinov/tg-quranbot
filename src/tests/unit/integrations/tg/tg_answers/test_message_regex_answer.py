# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from integrations.tg.tg_answers import TgMessageRegexAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer
from integrations.tg.update import TgUpdate
from settings import BASE_DIR


@pytest.fixture
def callback_update():
    return (BASE_DIR / 'tests' / 'fixtures' / 'button_callback.json').read_text()


async def test_on_message_update(message_update_factory):
    got = await TgMessageRegexAnswer(r'\d+:\d+', FkAnswer()).build(
        TgUpdate.str_ctor(message_update_factory('1:1', 1)),
    )

    assert got


async def test_on_callback_update(callback_update):
    got = await TgMessageRegexAnswer(r'\d+:\d+', FkAnswer()).build(TgUpdate(callback_update))

    assert not got
