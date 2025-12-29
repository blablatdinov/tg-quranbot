# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from app_types.fk_log_sink import FkLogSink
from app_types.fk_runable import FkRunable
from integrations.tg.app_with_get_me import AppWithGetMe


@pytest.fixture
def mock_http(respx_mock):
    respx_mock.get('https://api.telegram.org/botfakeToken/getMe')


@pytest.mark.usefixtures('mock_http')
async def test():
    await AppWithGetMe(
        FkRunable(),
        'fakeToken',
        FkLogSink(),
    ).run()
