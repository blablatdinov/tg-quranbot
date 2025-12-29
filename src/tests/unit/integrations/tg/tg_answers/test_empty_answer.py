# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from app_types.fk_update import FkUpdate
from integrations.tg.tg_answers import TgEmptyAnswer


async def test():
    got = await TgEmptyAnswer('token').build(FkUpdate.empty_ctor())

    assert got[0].url == 'https://api.telegram.org/bottoken/'


def test_str():
    assert 'superSecret' not in str(TgEmptyAnswer('superSecret'))
