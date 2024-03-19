"""The MIT License (MIT).

Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

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
import ujson

from integrations.tg.inline_query import InlineQuery, InlineQueryId
from integrations.tg.update import TgUpdate


@pytest.fixture()
def inline_query_update():
    return ujson.dumps({
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
            'query': 'Search',
            'offset': '',
        },
    })


def test(inline_query_update):
    got = str(InlineQuery(TgUpdate.str_ctor(inline_query_update)))

    assert got == 'Search'


def test_inline_query_id(inline_query_update):
    got = int(InlineQueryId(TgUpdate.str_ctor(inline_query_update)))

    assert got == 1540221937896102808
