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
from unittest.mock import AsyncMock

import pytest
from aioredis import Redis

from app_types.stringable import Stringable
from integrations.tg.tg_answers import FkAnswer
from services.reset_state_answer import ResetStateAnswer


class FkUpdate(Stringable):

    def __str__(self):
        return json.dumps({
            'from': {
                'chat_id': 123,
            },
        })


@pytest.fixture()
def mock_redis(mocker):
    mock = AsyncMock()
    Redis.set = mock  # type: ignore
    return mock


async def test_redis_query(mock_redis):
    await ResetStateAnswer(FkAnswer(), Redis()).build(FkUpdate())

    mock_redis.assert_called_with('123:step', 'nothing')


async def test_origin_answer_not_modificated(mock_redis):
    got = await ResetStateAnswer(FkAnswer(), Redis()).build(FkUpdate())
    origin = (await FkAnswer().build(FkUpdate()))[0].url

    assert got[0].url == origin
