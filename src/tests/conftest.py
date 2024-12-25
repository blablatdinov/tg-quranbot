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

import asyncio
import urllib
from pathlib import Path

import httpx
import pytest
from fakeredis import aioredis
from jinja2 import Template

from app_types.fk_log_sink import FkLogSink
from settings import BASE_DIR, Settings


# flake8: noqa: WPS202
@pytest.fixture
def unquote():
    def _unquote(url):  # noqa: WPS430
        return urllib.parse.unquote(
            str(url),
        ).replace('+', ' ')
    return _unquote


@pytest.fixture(scope='session')
def event_loop_policy():
    return asyncio.get_event_loop_policy()


@pytest.fixture
def fake_redis():
    return aioredis.FakeRedis()


@pytest.fixture
def message_update_factory():
    def _message_update_factory(text='', chat_id=1):  # noqa: WPS430
        return Template(
            (BASE_DIR / 'tests' / 'fixtures' / 'message_update.json').read_text(),
        ).render({'message_text': '"{0}"'.format(text), 'chat_id': chat_id})
    return _message_update_factory


@pytest.fixture
def callback_update_factory():
    def _message_update_factory(chat_id=1, callback_data=''):  # noqa: WPS430
        return Template(
            (BASE_DIR / 'tests/fixtures/button_callback.json').read_text(),
        ).render({'chat_id': chat_id, 'callback_data': callback_data})
    return _message_update_factory


@pytest.fixture
def inline_query_update_factory():
    def _inline_query_update_factory(query=''):  # noqa: WPS430
        return Template(
            (BASE_DIR / 'tests/fixtures/inline_query.json').read_text(),
        ).render({'query': query})
    return _inline_query_update_factory


@pytest.fixture
def fk_logger():
    return FkLogSink()


@pytest.fixture
def settings_ctor():
    def _settings_ctor(  # noqa: PLR0917, S107, WPS430, its settings ctor, not secure issue, pytest fixture specific
        redis_dsn='redis://default@localhost:6379/15',
        debug=True,
        database_url='postgresql://almazilaletdinov@localhost:5432/quranbot_test',
        api_token='',
        rabbitmq_user='',
        rabbitmq_pass='',
        rabbitmq_host='',
        rabbitmq_vhost='',
        daily_ayats=False,
        daily_prayers=False,
        ramadan_mode=False,
        sentry_dsn='',
        admin_chat_ids='1',
        telegram_client_id='',
        telegram_client_hash='',
        base_dir='',
    ):
        return Settings(
            REDIS_DSN=redis_dsn,
            DEBUG=debug,
            DATABASE_URL=database_url,
            API_TOKEN=api_token,
            RABBITMQ_USER=rabbitmq_user,
            RABBITMQ_PASS=rabbitmq_pass,
            RABBITMQ_HOST=rabbitmq_host,
            RABBITMQ_VHOST=rabbitmq_vhost,
            DAILY_AYATS=daily_ayats,
            DAILY_PRAYERS=daily_prayers,
            RAMADAN_MODE=ramadan_mode,
            SENTRY_DSN=sentry_dsn,
            ADMIN_CHAT_IDS=admin_chat_ids,
            TELEGRAM_CLIENT_ID=telegram_client_id,
            TELEGRAM_CLIENT_HASH=telegram_client_hash,
            BASE_DIR=base_dir,
        )
    return _settings_ctor


@pytest.fixture
def _mock_nominatim(respx_mock):
    respx_mock.get(
        'https://nominatim.openstreetmap.org/reverse.php?lat=55.7887&lon=49.1221&format=jsonv2',
    ).mock(return_value=httpx.Response(
        200,
        text=Path('src/tests/fixtures/nominatim_response.json').read_text(encoding='utf-8'),
    ))


@pytest.fixture
def settings():
    return Settings(_env_file=BASE_DIR.parent / '.env')
