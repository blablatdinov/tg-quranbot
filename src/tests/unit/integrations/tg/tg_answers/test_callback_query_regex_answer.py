# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from app_types.fk_log_sink import FkLogSink
from app_types.fk_update import FkUpdate
from integrations.tg.tg_answers import TgCallbackQueryRegexAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer


async def test():
    got = await TgCallbackQueryRegexAnswer('target', FkAnswer(), FkLogSink()).build(
        FkUpdate('{"callback_query":{"data":"target"}}'),
    )

    assert got[0].url == 'https://some.domain'


async def test_without_callback():
    got = await TgCallbackQueryRegexAnswer(
        'hello',
        FkAnswer(),
        FkLogSink(),
    ).build(FkUpdate.empty_ctor())

    assert got == []


async def test_not_match():
    got = await TgCallbackQueryRegexAnswer('target', FkAnswer(), FkLogSink()).build(
        FkUpdate('{"callback_query":{"data":"other_value"}}'),
    )

    assert got == []
