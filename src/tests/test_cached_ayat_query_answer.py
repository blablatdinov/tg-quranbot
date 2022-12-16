import json
from contextlib import suppress
from unittest.mock import AsyncMock

import pytest
from redis.asyncio import Redis

from app_types.stringable import ThroughStringable
from integrations.tg.tg_answers import TgAnswerInterface
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


async def test(update, mock_redis):
    with suppress(FakeError):
        await CachedAyatSearchQueryAnswer(TgAnswerFake(), mock_redis).build(ThroughStringable(update))

    mock_redis.set.assert_called_with('358610865:ayat_search_query', 'камни')
