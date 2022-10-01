from contextlib import suppress
from unittest.mock import AsyncMock

import pytest
from aioredis import Redis

from integrations.tg.tg_answers import TgAnswerInterface
from integrations.tg.tg_answers.update import Update
from services.ayats.search_by_text import CachedAyatSearchQueryAnswer


class FakeException(Exception):
    pass


class TgAnswerFake(TgAnswerInterface):

    async def build(self, update):
        raise FakeException


@pytest.fixture()
def mock_redis():
    redis = Redis()
    redis.set = AsyncMock()
    return redis


@pytest.fixture()
def update():
    return Update.parse_raw(
        """
        {
            "callback_query": null,
            "inline_query": null,
            "message": {
                "chat": {
                    "id": 358610865
                },
                "location_": null,
                "message_id": 22199,
                "text": "камни"
            },
            "update_id": 637462858
        }
        """
    )


async def test(update, mock_redis):
    mock_redis.set: AsyncMock
    with suppress(FakeException):
        await CachedAyatSearchQueryAnswer(TgAnswerFake(), mock_redis).build(update)

    mock_redis.set.assert_called_with('358610865:ayat_search_query', 'камни')

