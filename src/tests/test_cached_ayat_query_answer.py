from contextlib import suppress
from unittest.mock import AsyncMock

import pytest
from aioredis import Redis

from integrations.tg.tg_answers import TgAnswerInterface
from integrations.tg.tg_answers.update import Update
from services.ayats.cached_ayat_search_query import CachedAyatSearchQueryAnswer


class FakeError(Exception):
    pass


class TgAnswerFake(TgAnswerInterface):

    async def build(self, update):
        raise FakeError


@pytest.fixture()
def mock_redis():
    redis = Redis()
    redis.set = AsyncMock()  # type: ignore
    return redis


@pytest.fixture()
def update():
    update_json = """
    {
        "callback_query": null,
        "inline_query": null,
        "message": {
            "chat": {
                "id": 358610865
            },
            "location_": null,
            "message_id": 22199,
            "text": "камни",
            "date": 1666185977
        },
        "update_id": 637462858
    }
    """
    return Update.parse_raw(update_json)


async def test(update, mock_redis):
    with suppress(FakeError):
        await CachedAyatSearchQueryAnswer(TgAnswerFake(), mock_redis).build(update)

    mock_redis.set.assert_called_with('358610865:ayat_search_query', 'камни')
