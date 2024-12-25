# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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
from pytest_lazy_fixtures import lf

from app_types.fk_string import FkString
from integrations.tg.message_text import MessageText
from integrations.tg.update import TgUpdate


@pytest.fixture
def stringable_update(message_update_factory):
    return FkString(message_update_factory('afwe'))


@pytest.fixture
def stringable_callback_update(callback_update_factory):
    return callback_update_factory()


@pytest.mark.parametrize(('update', 'expected'), [
    (lf('stringable_update'), 'afwe'),
    (lf('stringable_callback_update'), 'awef'),
    ('{"message":{"text":"hello"}}', 'hello'),
])
def test(update, expected):
    got = MessageText(TgUpdate.str_ctor(update))

    assert str(got) == expected
