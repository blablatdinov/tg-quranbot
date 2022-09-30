import asyncio

from aioredis import Redis
import pytest

from services.user_state import UserState, UserStep


@pytest.fixture()
def mock_redis(mocker):
    future = asyncio.Future()
    future.set_result(None)
    mocker.patch('aioredis.Redis.get', return_value=future)


@pytest.mark.usefixtures('mock_redis')
async def test_not_exists_state():
    got = await UserState(Redis(), 879435).step()

    assert got == UserStep.nothing
