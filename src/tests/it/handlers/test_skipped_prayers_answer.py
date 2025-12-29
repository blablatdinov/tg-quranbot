# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest
import ujson

from app_types.fk_update import FkUpdate
from handlers.skipped_prayers_answer import SkippedPrayersAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer


@pytest.mark.usefixtures('_prayers_from_csv')
async def test(message_update_factory, pgsql):
    got = await SkippedPrayersAnswer(FkAnswer(), pgsql).build(
        FkUpdate(
            message_update_factory(chat_id=358610865, text='/skipped_prayers'),
        ),
    )

    assert got[0].url.params['text'] == '\n'.join([
        'Кол-во непрочитанных намазов:\n',
        'Иртәнге: 20',
        'Өйлә: 19',
        'Икенде: 20',
        'Ахшам: 19',
        'Ястү: 20',
    ])
    assert await pgsql.fetch_val(
        '\n'.join([
            'SELECT COUNT(*)',
            'FROM prayers_at_user AS pau',
            'WHERE pau.user_id = 358610865',
        ]),
    ) == 160
    assert ujson.loads(got[0].url.params['reply_markup']) == {
        'inline_keyboard': [
            [{'callback_data': 'decr(fajr)', 'text': 'Иртәнге: (-1)'}],
            [{'callback_data': 'decr(dhuhr)', 'text': 'Өйлә: (-1)'}],
            [{'callback_data': 'decr(asr)', 'text': 'Икенде: (-1)'}],
            [{'callback_data': 'decr(maghrib)', 'text': 'Ахшам: (-1)'}],
            [{'callback_data': 'decr(isha)', 'text': 'Ястү: (-1)'}],
        ],
    }


async def test_empty_prayers_at_user(pgsql, message_update_factory):
    got = await SkippedPrayersAnswer(FkAnswer(), pgsql).build(
        FkUpdate(
            message_update_factory(chat_id=358610865, text='/skipped_prayers'),
        ),
    )

    assert got[0].url.params['text'] == '\n'.join([
        'Кол-во непрочитанных намазов:\n',
        'Иртәнге: 0',
        'Өйлә: 0',
        'Икенде: 0',
        'Ахшам: 0',
        'Ястү: 0',
    ])
