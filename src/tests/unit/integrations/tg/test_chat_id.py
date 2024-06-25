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
from pytest_lazy_fixtures import lf

from integrations.tg.tg_chat_id import TgChatId
from integrations.tg.update import TgUpdate


@pytest.fixture()
def stringable_update(message_update_factory):
    return message_update_factory('', 358610865)


@pytest.fixture()
def stringable_callback_update(callback_update_factory):
    return callback_update_factory(chat_id=358610865)


@pytest.fixture()
def query_search_update(inline_query_update_factory):
    return inline_query_update_factory('adsfawef')


@pytest.mark.parametrize('update', [
    lf('stringable_update'),
    lf('stringable_callback_update'),
    lf('query_search_update'),
])
def test(update):
    chat_id = TgChatId(TgUpdate.str_ctor(update))

    assert int(chat_id) == 358610865
