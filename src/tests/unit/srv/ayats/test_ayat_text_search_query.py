# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from app_types.fk_log_sink import FkLogSink
from exceptions.content_exceptions import UserHasNotSearchQueryError
from srv.ayats.ayat_text_search_query import AyatTextSearchQuery


async def test_read(fake_redis):
    await fake_redis.set('1:ayat_search_query', b'value')

    assert await AyatTextSearchQuery(fake_redis, 1, FkLogSink()).read() == 'value'


async def test_read_without_value(fake_redis):
    with pytest.raises(UserHasNotSearchQueryError, match="User hasn't search query"):
        await AyatTextSearchQuery(fake_redis, 17, FkLogSink()).read()


async def test_write(fake_redis):
    await AyatTextSearchQuery(fake_redis, 84395, FkLogSink()).write('query')

    assert await fake_redis.get('84395:ayat_search_query') == b'query'
