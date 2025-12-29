# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from contextlib import suppress
from typing import final, override

import attrs
import pytest
import ujson

from app_types.fk_log_sink import FkLogSink
from integrations.tg.tg_answers import TgAnswer
from integrations.tg.update import TgUpdate
from srv.ayats.cached_ayat_search_query import CachedAyatSearchQueryAnswer


@final
@attrs.define(frozen=True)
class _FakeError(Exception):
    pass


@final
@attrs.define(frozen=True)
class _TgAnswerFake(TgAnswer):

    @override
    async def build(self, update):
        raise _FakeError


@pytest.fixture
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
    with suppress(_FakeError):
        await CachedAyatSearchQueryAnswer(
            _TgAnswerFake(), fake_redis, FkLogSink(),
        ).build(TgUpdate.str_ctor(update))

    assert await fake_redis.get('358610865:ayat_search_query') == 'камни'.encode()
