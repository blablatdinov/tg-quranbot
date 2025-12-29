# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from integrations.tg.fk_udpates_url import FkUpdatesURL
from integrations.tg.updates_long_polling_url import UpdatesLongPollingURL


def test() -> None:
    got = UpdatesLongPollingURL(
        FkUpdatesURL('https://fk.url'),
        0,
    ).generate(0)

    assert got == 'https://fk.url?timeout=0'
