"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import asyncio
import urllib

import pytest
from fakeredis import aioredis
from jinja2 import Template

from settings.settings import BASE_DIR


@pytest.fixture()
def unquote():
    def _unquote(url):  # noqa: WPS430
        return urllib.parse.unquote(
            str(url),
        ).replace('+', ' ')
    return _unquote


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    loop.slow_callback_duration = float('inf')
    yield loop
    loop.close()


@pytest.fixture()
def fake_redis():
    return aioredis.FakeRedis()


@pytest.fixture()
def message_update_factory():
    def _message_update_factory(text='', chat_id=1):  # noqa: WPS430
        return Template(
            (BASE_DIR / 'tests' / 'fixtures' / 'message_update.json').read_text(),
        ).render({'message_text': '"{0}"'.format(text), 'chat_id': chat_id})
    return _message_update_factory
