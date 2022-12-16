import asyncio

import pytest
from redis.asyncio import Redis

from services.user_state import UserState, UserStep


@pytest.fixture()
def mock_redis(mocker):
    future: asyncio.Future = asyncio.Future()
    future.set_result(None)
    mocker.patch('redis.asyncio.Redis.get', return_value=future)


@pytest.mark.usefixtures('mock_redis')
async def test_not_exists_state():
    got = await UserState(Redis(), 879435).step()

    assert got == UserStep.nothing
