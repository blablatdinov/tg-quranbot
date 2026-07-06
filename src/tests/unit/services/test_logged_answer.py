# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from app_types.fk_update import FkUpdate
from integrations.tg.fk_sendable import FkSendable
from services.logged_answer import LoggedAnswer
from srv.events.fk_sink import FkSink


async def test():
    got = await LoggedAnswer(
        FkSendable([]),
        FkSink(),
    ).send(FkUpdate.empty_ctor())

    assert got == []
