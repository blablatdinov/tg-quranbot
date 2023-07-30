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
from pyeo import elegant
import json
from pathlib import Path

import pytest
from pytest_lazyfixture import lazy_fixture

from integrations.tg.chat_id import TgChatId
from integrations.tg.update import TgUpdate


@pytest.fixture()
def stringable_update():
    return (Path(__file__).parent.parent / 'fixtures' / 'message_update.json').read_text()


@pytest.fixture()
def stringable_callback_update():
    return (Path(__file__).parent.parent / 'fixtures' / 'button_callback.json').read_text()


@pytest.fixture()
def query_search_update():
    return json.dumps({
        'update_id': 637463119,
        'inline_query': {
            'id': '1540221937896102808',
            'from': {
                'id': 358610865,
                'is_bot': False,
                'first_name': 'Almaz',
                'last_name': 'Ilaletdinov',
                'username': 'ilaletdinov',
                'language_code': 'ru',
            },
            'chat_type': 'sender',
            'query': 'adsfawef',
            'offset': '',
        },
    })


@pytest.mark.parametrize('input_', [
    lazy_fixture('stringable_update'),
    lazy_fixture('stringable_callback_update'),
    lazy_fixture('query_search_update'),
])
def test(input_):
    chat_id = TgChatId(TgUpdate(input_))

    assert int(chat_id) == 358610865
