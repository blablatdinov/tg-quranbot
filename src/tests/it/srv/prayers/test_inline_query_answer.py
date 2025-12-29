# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import uuid

import pytest
import ujson

from app_types.fk_update import FkUpdate
from exceptions.internal_exceptions import NotProcessableUpdateError
from integrations.tg.tg_answers.fk_answer import FkAnswer
from srv.prayers.inline_query_answer import InlineQueryAnswer


@pytest.fixture
async def _db_city(city_factory):
    await city_factory(str(uuid.uuid4()), 'Kazan')


@pytest.mark.usefixtures('_db_city')
async def test(pgsql):
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


@pytest.mark.usefixtures('_db_city')
async def test_not_processable(pgsql):
    with pytest.raises(NotProcessableUpdateError):
        await InlineQueryAnswer(FkAnswer(), pgsql).build(
            FkUpdate(ujson.dumps({
                'update_id': 1,
                'chat': {'id': 1},
            })),
        )
