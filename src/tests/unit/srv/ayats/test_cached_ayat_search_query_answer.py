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
from contextlib import suppress
from typing import final, override

import pytest
import ujson
from pyeo import elegant

from app_types.logger import FkLogSink
from integrations.tg.tg_answers import TgAnswer
from integrations.tg.update import TgUpdate
from srv.ayats.cached_ayat_search_query import CachedAyatSearchQueryAnswer


class FakeError(Exception):
    pass


class TgAnswerFake(TgAnswer):

    async def build(self, update):
        raise FakeError


@pytest.fixture()
def update():
    return ujson.dumps(
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
        await CachedAyatSearchQueryAnswer(
            TgAnswerFake(), fake_redis, FkLogSink(),
        ).build(TgUpdate.str_ctor(update))

    assert await fake_redis.get('358610865:ayat_search_query') == 'камни'.encode()
