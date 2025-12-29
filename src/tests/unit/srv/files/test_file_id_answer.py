# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.fk_update import FkUpdate
from integrations.tg.tg_answers import TgAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer
from srv.files.file_id_answer import TelegramFileIdAnswer
from srv.files.fk_file import FkFile


@final
@attrs.define(frozen=True)
class FakeAnswer(TgAnswer):

    @override
    async def build(self, update):
        return [
            httpx.Request('GET', 'https://some.domain'),
        ]


async def test():
    got = await TelegramFileIdAnswer(
        FkAnswer(), FkFile('file_id', ''),
    ).build(FkUpdate.empty_ctor())

    assert got[0].url.query.decode('utf-8') == 'audio=file_id'
