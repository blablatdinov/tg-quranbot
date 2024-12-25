# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

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
