# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
import ujson

from app_types.fk_log_sink import FkLogSink
from app_types.fk_update import FkUpdate
from app_types.update import Update
from exceptions.content_exceptions import UserHasNotCityIdError
from integrations.tg.tg_answers import TgAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer
from srv.prayers.invite_set_city_answer import InviteSetCityAnswer
from srv.prayers.user_without_city_safe_answer import UserWithoutCitySafeAnswer


@final
@attrs.define(frozen=True)
class FkOrigin(TgAnswer):

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        raise UserHasNotCityIdError


async def test_exception():
    got = await UserWithoutCitySafeAnswer(FkOrigin(), FkAnswer()).build(FkUpdate.empty_ctor())

    assert got[0].url == 'https://some.domain'


async def test_invite_set_city_answer(fake_redis):
    got = await InviteSetCityAnswer(
        FkAnswer(), fake_redis, FkLogSink(),
    ).build(FkUpdate('{"chat":{"id":1}}'))

    assert got[0].url.params['reply_markup'] == ujson.dumps({
        'inline_keyboard': [[
            {'text': 'Поиск города', 'switch_inline_query_current_chat': ''},
        ]],
    })
