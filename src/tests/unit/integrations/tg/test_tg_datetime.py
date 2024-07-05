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

import datetime

import pytest
import pytz
from pytest_lazy_fixtures import lf

from app_types.fk_string import FkString
from integrations.tg.tg_datetime import TgDateTime
from integrations.tg.update import TgUpdate


@pytest.fixture
def message_update(message_update_factory):
    return FkString(message_update_factory())


@pytest.fixture
def stringable_callback_update(callback_update_factory):
    return callback_update_factory()


@pytest.mark.parametrize(('update', 'expected'), [
    (
        lf('message_update'),
        datetime.datetime(2022, 12, 9, 10, 20, 13, tzinfo=pytz.timezone('UTC')),
    ),
    (
        lf('stringable_callback_update'),
        datetime.datetime(2022, 10, 30, 15, 54, 34, tzinfo=pytz.timezone('UTC')),
    ),
])
def test(update, expected):
    tg_datetime = TgDateTime(TgUpdate.str_ctor(update))

    assert tg_datetime.datetime() == expected
