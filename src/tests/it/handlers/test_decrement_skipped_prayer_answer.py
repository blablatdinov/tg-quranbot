# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest
import ujson

from app_types.fk_update import FkUpdate
from handlers.decrement_skipped_prayer_answer import DecrementSkippedPrayerAnswer
from integrations.tg.tg_answers.fk_answer import FkAnswer


@pytest.mark.usefixtures('_prayers_from_csv')
async def test(callback_update_factory, pgsql):
    got = await DecrementSkippedPrayerAnswer(FkAnswer(), pgsql).build(
        FkUpdate(callback_update_factory(chat_id=358610865, callback_data='decr(fajr)')),
    )

    assert got[0].url.path == '/editMessageText'
    assert got[0].url.params['text'] == '\n'.join([
        'Кол-во непрочитанных намазов:\n',
        'Иртәнге: 19',
        'Өйлә: 19',
        'Икенде: 20',
        'Ахшам: 19',
        'Ястү: 20',
    ])
    assert await pgsql.fetch_val(
        '\n'.join([
            'SELECT COUNT(*)',
            'FROM prayers_at_user AS pau',
            "WHERE pau.user_id = 358610865 AND pau.is_read = 't'",
        ]),
    ) == 63
    assert ujson.loads(got[0].url.params['reply_markup']) == {
        'inline_keyboard': [
            [{'callback_data': 'decr(fajr)', 'text': 'Иртәнге: (-1)'}],
            [{'callback_data': 'decr(dhuhr)', 'text': 'Өйлә: (-1)'}],
            [{'callback_data': 'decr(asr)', 'text': 'Икенде: (-1)'}],
            [{'callback_data': 'decr(maghrib)', 'text': 'Ахшам: (-1)'}],
            [{'callback_data': 'decr(isha)', 'text': 'Ястү: (-1)'}],
        ],
    }
