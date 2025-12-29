# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.fk_update import FkUpdate
from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer
from srv.ayats.favorite_ayat_empty_safe import FavoriteAyatEmptySafeAnswer


@final
@attrs.define(frozen=True)
class IndexErrorAnswer(TgAnswer):

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        raise IndexError


async def test():
    got = await FavoriteAyatEmptySafeAnswer(
        FkAnswer('http://right-way.com'),
        FkAnswer('http://error-way.com'),
    ).build(FkUpdate.empty_ctor())

    assert str(got[0].url) == 'http://right-way.com'


async def test_error():
    got = await FavoriteAyatEmptySafeAnswer(
        IndexErrorAnswer(),
        FkAnswer(),
    ).build(FkUpdate.empty_ctor())

    assert str(got[0].url) == 'https://some.domain'
