# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final

import httpx

from app_types.fk_log_sink import FkLogSink
from app_types.fk_update import FkUpdate
from app_types.update import Update
from integrations.tg.default_backoff import DefaultBackoff
from integrations.tg.retried_sendable import RetriedSendable
from integrations.tg.sendable import Sendable


@final
class SeSendable(Sendable):

    # def __init__(self, attempts):
    #     self._attempts = attempts
    #     self._current = 1

    async def send(self, update: Update) -> list[dict]:
        # self._current += 1
        raise httpx.ConnectTimeout('message')


async def test():
    await RetriedSendable(
        SeSendable(),
        FkLogSink(),
        5,
        DefaultBackoff(),
    ).send(FkUpdate.empty_ctor())
