# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import uuid

import httpx
import pytest
from eljson.json_doc import JsonDoc

from app_types.fk_log_sink import FkLogSink
from integrations.tg.tg_answers import TgEmptyAnswer
from srv.events.fk_sink import FkSink
from srv.events.mailing_created import MailingCreatedEvent


@pytest.fixture
def _mock_http(respx_mock):
    respx_mock.get('https://api.telegram.org/bottoken/sendMessage?chat_id=483457&text=Hello&parse_mode=html').mock(
        return_value=httpx.Response(
            json={
                'ok': True,
                'result': {
                    'message_id': 52551,
                    'from': {
                        'id': 452230948,
                        'is_bot': True,
                        'first_name': 'WokeUpSmiled',
                        'username': 'WokeUpSmiled_bot',
                    },
                    'chat': {
                        'id': 358610865,
                        'first_name': 'Алмаз',
                        'last_name': 'Илалетдинов',
                        'username': 'ilaletdinov',
                        'type': 'private',
                    },
                    'date': 1710448509,
                    'text': 'Hello',
                },
            },
            status_code=200,
        ),
    )


@pytest.fixture
async def _user(user_factory):
    await user_factory(483457)


@pytest.mark.usefixtures('_mock_http', '_user')
async def test(pgsql, settings_ctor):
    await MailingCreatedEvent(
        TgEmptyAnswer('token'),
        pgsql,
        FkSink(),
        FkLogSink(),
        settings_ctor(admin_chat_ids='93754').ADMIN_CHAT_IDS,
    ).process(
        JsonDoc({'data': {
            'mailing_id': str(uuid.uuid4()),
            'text': 'Hello',
            'group': 'all',
        }}),
    )
