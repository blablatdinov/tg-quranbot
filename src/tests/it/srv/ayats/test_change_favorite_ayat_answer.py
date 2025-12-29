# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest
import ujson

from app_types.fk_log_sink import FkLogSink
from app_types.fk_update import FkUpdate
from integrations.tg.tg_answers.fk_answer import FkAnswer
from srv.ayats.change_favorite_ayat_answer import ChangeFavoriteAyatAnswer


@pytest.fixture
async def _user(user_factory):
    await user_factory(1)


@pytest.mark.usefixtures('db_ayat', '_user')
async def test_add(pgsql, fake_redis):
    got = await ChangeFavoriteAyatAnswer(
        pgsql, FkAnswer(), fake_redis, FkLogSink(),
    ).build(FkUpdate(
        ujson.dumps({
            'callback_query': {'data': 'addToFavor(1)'},
            'chat': {'id': 1},
            'message': {'message_id': 1},
        }),
    ))

    assert ujson.loads(got[0].url.params['reply_markup']) == {
        'inline_keyboard': [
            [{'callback_data': 'fake', 'text': 'стр. 1/1'}],
            [{'callback_data': 'removeFromFavor(1)', 'text': 'Удалить из избранного'}],
        ],
    }


@pytest.mark.usefixtures('db_ayat', '_user')
async def test_remove(pgsql, fake_redis):
    got = await ChangeFavoriteAyatAnswer(
        pgsql, FkAnswer(), fake_redis, FkLogSink(),
    ).build(FkUpdate(
        ujson.dumps({
            'callback_query': {'data': 'removeFromFavor(1)'},
            'chat': {'id': 1},
            'message': {'message_id': 1},
        }),
    ))

    assert ujson.loads(got[0].url.params['reply_markup']) == {
        'inline_keyboard': [
            [{'callback_data': 'fake', 'text': 'стр. 1/1'}],
            [{'callback_data': 'addToFavor(1)', 'text': 'Добавить в избранное'}],
        ],
    }
