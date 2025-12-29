# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest
import ujson

from app_types.fk_log_sink import FkLogSink
from app_types.fk_update import FkUpdate
from handlers.pg_set_user_city_answer import PgSetUserCityAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer


async def test_message(pgsql, fake_redis):
    debug = False
    got = await PgSetUserCityAnswer(pgsql, FkAnswer(), debug, fake_redis, FkLogSink()).build(
        FkUpdate(ujson.dumps({
            'message': {'text': 'Kazan'},
            'chat': {'id': 384957},
        })),
    )

    assert got[0].url.params['text'] == 'Этот город не поддерживается'


@pytest.mark.usefixtures('_mock_nominatim')
async def test_location(pgsql, fake_redis):
    debug = False
    got = await PgSetUserCityAnswer(pgsql, FkAnswer(), debug, fake_redis, FkLogSink()).build(
        FkUpdate(ujson.dumps({
            'chat': {'id': 34847935},
            'latitude': 55.7887,
            'longitude': 49.1221,
        })),
    )

    assert got[0].url.params['text'] == 'Этот город не поддерживается'
