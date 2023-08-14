"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import pytest
from pytest_lazyfixture import lazy_fixture

from app_types.stringable import ThroughString
from integrations.tg.update import TgUpdate
from integrations.tg.update_id import UpdateId
from settings import settings


@pytest.fixture()
def stringable_update():
    return ThroughString(
        (settings.BASE_DIR / 'tests' / 'fixtures' / 'message_update.json').read_text(),
    )


@pytest.fixture()
def stringable_callback_update():
    return ThroughString(
        (settings.BASE_DIR / 'tests' / 'fixtures' / 'button_callback.json').read_text(),
    )


@pytest.mark.parametrize('input_,expected', [
    (lazy_fixture('stringable_update'), 637463103),
    (lazy_fixture('stringable_callback_update'), 637463104),
])
def test(input_, expected):
    update_id = UpdateId(TgUpdate(input_))

    assert int(update_id) == expected
