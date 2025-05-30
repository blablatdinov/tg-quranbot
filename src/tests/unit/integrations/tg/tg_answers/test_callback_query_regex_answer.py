# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

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
