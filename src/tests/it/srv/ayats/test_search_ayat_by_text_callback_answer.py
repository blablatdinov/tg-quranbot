# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

import pytest
import ujson

from app_types.logger import FkLogSink
from app_types.update import FkUpdate
from exceptions.content_exceptions import AyatNotFoundError
from integrations.tg.chat_id import FkChatId
from integrations.tg.tg_answers import FkAnswer
from srv.ayats.ayat_text_search_query import AyatTextSearchQuery
from srv.ayats.search_ayat_by_text_callback_answer import SearchAyatByTextCallbackAnswer


@pytest.fixture()
def search_answer(pgsql, fake_redis):
    debug = True
    return SearchAyatByTextCallbackAnswer(debug, FkAnswer(), fake_redis, pgsql, FkLogSink())


@pytest.mark.usefixtures('db_ayat')
async def test(fake_redis, unquote, search_answer):
    await AyatTextSearchQuery(fake_redis, FkChatId(1758), FkLogSink()).write('Content')
    got = await search_answer.build(FkUpdate('{"callback_query": {"data": "1"}, "chat": {"id": 1758}}'))

    assert got[0].url.path == '/sendMessage'
    assert dict(got[0].url.params) == {
        'parse_mode': 'html',
        'chat_id': '1758',
        'text': '\n'.join([
            '<a href="https://umma.ru/link-to-sura#1-1">1:1-7)</a>',
            'Arab text\n',
            'Content\n',
            '<i>Transliteration</i>',
        ]),
        'reply_markup': ujson.dumps({
            'inline_keyboard': [
                [{'text': 'стр. 1/1', 'callback_data': 'fake'}],
                [{'text': 'Добавить в избранное', 'callback_data': 'addToFavor(1)'}],
            ],
        }),
        'link_preview_options': '{"is_disabled":true}',
    }


@pytest.mark.usefixtures('db_ayat')
async def test_unknown_target_ayat(fake_redis, search_answer):
    await AyatTextSearchQuery(fake_redis, 1758, FkLogSink()).write('Content')
    with pytest.raises(AyatNotFoundError):
        await search_answer.build(FkUpdate('{"callback_query": {"data": "2"}, "chat": {"id": 1758}}'))
