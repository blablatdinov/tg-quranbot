import json
from unittest.mock import AsyncMock

import pytest
from redis.asyncio import Redis

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
