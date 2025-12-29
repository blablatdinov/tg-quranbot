# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import httpx
import pytest
from eljson.json_doc import JsonDoc

from app_types.fk_log_sink import FkLogSink
from integrations.tg.tg_answers import TgEmptyAnswer
from srv.events.fk_sink import FkSink
from srv.events.message_deleted import MessageDeleted


@pytest.fixture
def _mock_http(respx_mock):
    respx_mock.get('https://api.telegram.org/bottoken/deleteMessage?chat_id=37945&message_id=893457').mock(
        return_value=httpx.Response(
            text='{"ok":true}',
            status_code=200,
        ),
    )


@pytest.mark.usefixtures('_mock_http')
async def test(pgsql):
    await MessageDeleted(
        TgEmptyAnswer('token'),
        pgsql,
        FkSink(),
        FkLogSink(),
    ).process(JsonDoc({'data': {'chat_id': 37945, 'message_id': 893457}}))
