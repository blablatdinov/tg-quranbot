# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import httpx
import pytest
import ujson
from eljson.json_doc import JsonDoc

from app_types.fk_log_sink import FkLogSink
from integrations.tg.tg_answers.fk_answer import FkAnswer
from srv.events.check_user_status import CheckUsersStatus
from srv.events.fk_sink import FkSink


@pytest.fixture
def _mock_actives(respx_mock):
    rv = {
        'return_value': httpx.Response(
            200, text=ujson.dumps({'ok': True, 'result': True}),
        ),
    }
    respx_mock.get('https://some.domain/sendChatAction?chat_id=1&action=typing').mock(**rv)
    respx_mock.get('https://some.domain/sendChatAction?chat_id=2&action=typing').mock(**rv)
    respx_mock.get('https://some.domain/sendChatAction?chat_id=3&action=typing').mock(**rv)


@pytest.fixture
def _mock_unsubscribed(respx_mock):
    rv = {
        'return_value': httpx.Response(
            400, text='{"ok":false,"error_code":400,"description":"Bad Request: chat not found"}',
        ),
    }
    respx_mock.get('https://some.domain/sendChatAction?chat_id=1&action=typing').mock(**rv)
    respx_mock.get('https://some.domain/sendChatAction?chat_id=2&action=typing').mock(**rv)
    respx_mock.get('https://some.domain/sendChatAction?chat_id=3&action=typing').mock(
        return_value=httpx.Response(200, text=ujson.dumps({'ok': True, 'result': True})),
    )


@pytest.fixture
async def _users(user_factory):
    await user_factory(1)
    await user_factory(2)
    await user_factory(3)


@pytest.mark.usefixtures('_users', '_mock_actives')
async def test_user_status(pgsql):
    await CheckUsersStatus(
        FkAnswer(), pgsql, FkSink(), FkLogSink(),
    ).process(JsonDoc({}))

    assert [
        row['is_active']
        for row in await pgsql.fetch_all('SELECT is_active FROM users')
    ] == [True, True, True]


@pytest.mark.usefixtures('_users', '_mock_unsubscribed')
async def test_unsubscribed(pgsql):
    await CheckUsersStatus(
        FkAnswer(), pgsql, FkSink(), FkLogSink(),
    ).process(JsonDoc({}))

    assert [
        (row['chat_id'], row['is_active'])
        for row in await pgsql.fetch_all('SELECT chat_id, is_active FROM users ORDER BY chat_id')
    ] == [(1, False), (2, False), (3, True)]
