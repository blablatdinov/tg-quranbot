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
import json
from contextlib import suppress
from typing import final

import pytest
from fakeredis import aioredis
from pyeo import elegant

from integrations.tg.tg_answers import TgAnswer
from integrations.tg.update import TgUpdate
from srv.ayats.cached_ayat_search_query import CachedAyatSearchQueryAnswer


class FakeError(Exception):
    pass


@elegant
@final
class TgAnswerFake(TgAnswer):

    async def build(self, update):
        raise FakeError


@pytest.fixture()
def fake_redis():
    return aioredis.FakeRedis()


@pytest.fixture()
def update():
    return json.dumps(
        {
            'callback_query': None,
            'inline_query': None,
            'message': {
                'chat': {
                    'id': 358610865,
                },
                'location_': None,
                'message_id': 22199,
                'text': 'камни',
                'date': 1666185977,
            },
            'update_id': 637462858,
        },
        ensure_ascii=False,
    )


async def test(update, fake_redis):
    with suppress(FakeError):
        await CachedAyatSearchQueryAnswer(TgAnswerFake(), fake_redis).build(TgUpdate(update))

    assert (await fake_redis.get('358610865:ayat_search_query')).decode('utf-8') == 'камни'
