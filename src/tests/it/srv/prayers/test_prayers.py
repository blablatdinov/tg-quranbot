# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import uuid

import pytest

from app_types.fk_log_sink import FkLogSink
from app_types.fk_update import FkUpdate
from handlers.pg_prayer_time_answer import PgPrayerTimeAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer


@pytest.fixture
async def _user(city_factory, user_factory):
    city_id = str(uuid.uuid4())
    city = await city_factory(city_id, 'Казань')
    await user_factory(123, city=city)


@pytest.mark.usefixtures('_user')
async def test_not_found_prayer(pgsql, fake_redis, time_machine, settings_ctor):
    time_machine.move_to('2023-08-30')
    got = await PgPrayerTimeAnswer.new_prayers_ctor(
        pgsql, FkAnswer(), [321], fake_redis, FkLogSink(), settings_ctor(ramadan_mode=True),
    ).build(FkUpdate('{"chat":{"id":123},"message":{"message_id":1,"text":"Время намаза"}}'))

    assert len(got) == 2
    assert got[0].url.path == got[1].url.path == '/sendMessage'
    assert dict(got[0].url.params) == {
        'chat_id': '123',
        'text': 'Время намаза на 30.08.2023 для города Казань не найдено',
    }
    assert dict(got[1].url.params) == {
        'chat_id': '321',
        'text': 'Время намаза на 30.08.2023 для города Казань не найдено',
    }
