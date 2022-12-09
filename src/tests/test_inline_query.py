import json

import pytest

from integrations.tg.inline_query import InlineQuery, InlineQueryId


@pytest.fixture()
def inline_query_update():
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
            'query': 'Search',
            'offset': '',
        },
    })


def test(inline_query_update):
    got = str(InlineQuery(inline_query_update))

    assert got == 'Search'


def test_inline_query_id(inline_query_update):
    got = int(InlineQueryId(inline_query_update))

    assert got == 1540221937896102808
