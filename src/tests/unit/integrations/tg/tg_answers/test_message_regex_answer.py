# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

import pytest

from integrations.tg.tg_answers import FkAnswer, TgMessageRegexAnswer
from integrations.tg.update import TgUpdate
from settings import BASE_DIR


@pytest.fixture()
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
