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
# flake8: noqa: WPS202
from pathlib import Path

import pytest


@pytest.fixture()
def _user(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, '/start')
    wait_until(tg_client, 3)


@pytest.fixture()
def _favor_ayats(db_conn):
    cursor = db_conn.cursor()
    for ayat_id in (671, 3383, 1829, 409):
        cursor.execute(
            'INSERT INTO favorite_ayats (ayat_id, user_id) VALUES (%s, %s)',
            (ayat_id, 5354079702),
        )


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_user', '_favor_ayats')
def test_get_favors(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, 'Избранное')
    last_messages = wait_until(tg_client, 6)

    assert (
        last_messages[1].message.strip()
        == Path('src/tests/e2e/fixtures/3_133_ayat.txt').read_text().strip()
    )
    assert [
        (button.text, button.data)
        for button_row in last_messages[1].get_buttons()
        for button in button_row
    ] == [
        ('стр. 1/4', b'fake'),
        ('5:19 ->', b'getFAyat(671)'),
        ('Удалить из избранного', b'removeFromFavor(409)'),
    ]


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_user', '_favor_ayats')
@pytest.mark.flaky(retries=3)
def test_paginate_forward(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, 'Избранное')
    last_messages = wait_until(tg_client, 6)
    next(
        button
        for button_row in last_messages[1].get_buttons()
        for button in button_row
        if button.text == '5:19 ->'
    ).click()
    last_messages = wait_until(tg_client, 8)

    assert [
        (button.text, button.data)
        for button_row in last_messages[1].get_buttons()
        for button in button_row
    ] == [
        ('<- 3:133', b'getFAyat(409)'),
        ('стр. 2/4', b'fake'),
        ('15:85 ->', b'getFAyat(1829)'),
        ('Удалить из избранного', b'removeFromFavor(671)'),
    ]


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_user', '_favor_ayats')
@pytest.mark.flaky(retries=3)
def test_paginate_backward(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, 'Избранное')
    last_messages = wait_until(tg_client, 6)
    next(
        button
        for button_row in last_messages[1].get_buttons()
        for button in button_row
        if button.text == '5:19 ->'
    ).click()
    last_messages = wait_until(tg_client, 8)
    next(
        button
        for button_row in last_messages[1].get_buttons()
        for button in button_row
        if button.text == '<- 3:133'
    ).click()
    last_messages = wait_until(tg_client, 10)

    assert [
        (button.text, button.data)
        for button_row in last_messages[1].get_buttons()
        for button in button_row
    ] == [
        ('стр. 1/4', b'fake'),
        ('5:19 ->', b'getFAyat(671)'),
        ('Удалить из избранного', b'removeFromFavor(409)'),
    ]


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_user')
@pytest.mark.flaky(retries=3)
def test_add_to_favor(tg_client, bot_name, wait_until, db_query_vals):
    tg_client.send_message(bot_name, '8:7')
    last_messages = wait_until(tg_client, 6)
    last_messages[1].get_buttons()[1][0].click()
    last_messages = wait_until(tg_client, 6)

    assert [
        (button.text, button.data)
        for button_row in last_messages[1].get_buttons()
        for button in button_row
    ] == [
        ('<- 8:6', b'getAyat(1144)'),
        ('стр. 1145/5737', b'fake'),
        ('8:8 ->', b'getAyat(1146)'),
        ('Удалить из избранного', b'removeFromFavor(1145)'),
    ]
    assert db_query_vals('SELECT * FROM favorite_ayats') == [(1145, 5354079702)]


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_user', '_favor_ayats')
@pytest.mark.flaky(retries=3)
def test_remove_from_favor(tg_client, bot_name, wait_until, db_query_vals):
    tg_client.send_message(bot_name, '3:133')
    last_messages = wait_until(tg_client, 6)
    last_messages[1].get_buttons()[1][0].click()
    last_messages = wait_until(tg_client, 6)

    assert [
        (button.text, button.data)
        for button_row in last_messages[1].get_buttons()
        for button in button_row
    ] == [
        ('<- 3:132', b'getAyat(408)'),
        ('стр. 409/5737', b'fake'),
        ('3:134 ->', b'getAyat(410)'),
        ('Добавить в избранное', b'addToFavor(409)'),
    ]
    assert len(db_query_vals('SELECT * FROM favorite_ayats')) == 3


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_user', '_favor_ayats')
@pytest.mark.flaky(retries=3)
def test_remove_from_favor_in_favor_pagination(tg_client, bot_name, wait_until, db_query_vals):
    tg_client.send_message(bot_name, 'Избранное')
    last_messages = wait_until(tg_client, 6)
    assert [
        (button.text, button.data)
        for button_row in last_messages[1].get_buttons()
        for button in button_row
    ] == [
        ('стр. 1/4', b'fake'),
        ('5:19 ->', b'getFAyat(671)'),
        ('Удалить из избранного', b'removeFromFavor(409)'),
    ]
    last_messages[1].get_buttons()[1][0].click()
    last_messages = wait_until(tg_client, 6)

    assert len(db_query_vals('SELECT * FROM favorite_ayats')) == 3
    assert [
        (button.text, button.data)
        for button_row in last_messages[1].get_buttons()
        for button in button_row
    ] == [
        ('стр. 1/4', b'fake'),
        ('5:19 ->', b'getFAyat(671)'),
        ('Добавить в избранное', b'addToFavor(409)'),
    ]
