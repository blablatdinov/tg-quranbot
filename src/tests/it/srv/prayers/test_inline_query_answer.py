"""The MIT License (MIT).

Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import uuid

import pytest
import ujson

from app_types.update import FkUpdate
from exceptions.internal_exceptions import NotProcessableUpdateError
from integrations.tg.tg_answers import FkAnswer
from srv.prayers.inline_query_answer import InlineQueryAnswer


@pytest.fixture()
async def _db_cities(pgsql):
    await pgsql.execute(
        'INSERT INTO cities (city_id, name) VALUES (:city_id, :name)',
        {'city_id': str(uuid.uuid4()), 'name': 'Kazan'},
    )


@pytest.mark.usefixtures('_db_cities')
async def test(pgsql, unquote):
    got = await InlineQueryAnswer(FkAnswer(), pgsql).build(
        FkUpdate(ujson.dumps({
            'update_id': 1,
            'query': 'Kazan',
            'chat': {'id': 1},
            'inline_query': {'id': 1},
        })),
    )

    assert ujson.loads(got[0].url.params['results']) == [
        {
            'id': '0',
            'type': 'article',
            'title': 'Kazan',
            'input_message_content': {'message_text': 'Kazan'},
        },
    ]


@pytest.mark.usefixtures('_db_cities')
async def test_not_processable(pgsql, unquote):
    with pytest.raises(NotProcessableUpdateError):
        await InlineQueryAnswer(FkAnswer(), pgsql).build(
            FkUpdate(ujson.dumps({
                'update_id': 1,
                'chat': {'id': 1},
            })),
        )
