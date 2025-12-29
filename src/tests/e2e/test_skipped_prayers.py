# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from itertools import chain
from pathlib import Path

import pytest


@pytest.fixture
def _prayers(db_conn):
    lines = [
        line.split(';')
        for line in Path('src/tests/fixtures/prayers.csv').read_text(encoding='utf-8').splitlines()
    ]
    cursor = db_conn.cursor()
    cursor.execute('\n'.join([
        'INSERT INTO users (chat_id, city_id, is_active) VALUES',
        "(5354079702, 'bc932b25-707e-4af1-8b6e-facb5e6dfa9b', true)",
    ]))
    lines = [
        line.split(';')
        for line in Path('src/tests/fixtures/prayers_at_user.csv').read_text(encoding='utf-8').splitlines()
    ]
    query = '\n'.join([
        'INSERT INTO prayers_at_user (prayer_at_user_id, user_id, prayer_id, is_read)',
        'VALUES',
        ',\n'.join([
            "('{0}', 5354079702, {1}, {2})".format(
                int(line[0]),
                int(line[3]),
                line[4] == 'true',
            )
            for line in lines
        ]),
    ])
    cursor.execute(query)


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_prayers')
def test_skipped_prayers(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, '/skipped_prayers')
    messages = wait_until(tg_client, 2)

    assert [
        (button.text, button.data)
        for button_row in messages[0].get_buttons()
        for button in button_row
    ] == [
        ('Иртәнге: (-1)', b'decr(fajr)'),
        ('Өйлә: (-1)', b'decr(dhuhr)'),
        ('Икенде: (-1)', b'decr(asr)'),
        ('Ахшам: (-1)', b'decr(maghrib)'),
        ('Ястү: (-1)', b'decr(isha)'),
    ]
    assert messages[0].message == '\n'.join([
        'Кол-во непрочитанных намазов:\n',
        'Иртәнге: 20',
        'Өйлә: 19',
        'Икенде: 20',
        'Ахшам: 19',
        'Ястү: 20',
    ])


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_prayers')
@pytest.mark.flaky(retries=3)
def test_mark_readed(tg_client, bot_name, wait_until, db_query_vals):
    tg_client.send_message(bot_name, '/skipped_prayers')
    messages = wait_until(tg_client, 2)
    next(chain.from_iterable(
        button_row for button_row in messages[0].get_buttons()
    )).click()
    messages = wait_until(tg_client, 2)

    assert db_query_vals(
        'SELECT is_read FROM prayers_at_user AS pau WHERE pau.prayer_at_user_id = 511037',
    ) == [(True,)]
    assert messages[0].message == '\n'.join([
        'Кол-во непрочитанных намазов:\n',
        'Иртәнге: 19',
        'Өйлә: 19',
        'Икенде: 20',
        'Ахшам: 19',
        'Ястү: 20',
    ])
    assert [
        (button.text, button.data)
        for button_row in messages[0].get_buttons()
        for button in button_row
    ] == [
        ('Иртәнге: (-1)', b'decr(fajr)'),
        ('Өйлә: (-1)', b'decr(dhuhr)'),
        ('Икенде: (-1)', b'decr(asr)'),
        ('Ахшам: (-1)', b'decr(maghrib)'),
        ('Ястү: (-1)', b'decr(isha)'),
    ]
