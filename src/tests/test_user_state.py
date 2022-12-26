from unittest.mock import AsyncMock

import pytest
from redis.asyncio import Redis

from services.user_state import UserState, UserStep


@pytest.fixture()
def mock_redis(mocker):
    mock = AsyncMock(return_value=None)
    Redis.get = mock  # type: ignore
    return mock


@pytest.mark.usefixtures('mock_redis')
async def test_not_exists_state(mock_redis):
    got = await UserState(Redis(), 879435).step()

    assert got == UserStep.nothing
    mock_redis.assert_called_with('879435:step')
