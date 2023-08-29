"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

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
from pathlib import Path

import pytest


@pytest.fixture()
def user(tg_client, db_conn, bot_name, wait_until):
    tg_client.send_message(bot_name, '/start')
    wait_until(tg_client, 3)


@pytest.mark.usefixtures('bot_process', 'clear_db')
def test_get_favors(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, 'Избранное')
    last_messages = wait_until(tg_client, 3)
    print([
        (button.text, button.data)
        for button_row in last_messages[1].get_buttons()
        for button in button_row
    ])
    assert false

    assert last_messages[1].message == path(expected).read_text()


@pytest.mark.usefixtures('bot_process', 'clear_db', 'user')
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
        ('<- 8:6', b'getAyat(1144)'), ('стр. 1145/5737', b'fake'), ('8:8 ->', b'getAyat(1146)'),
        ('Удалить из избранного', b'removeFromFavor(1145)'),
    ]
    assert db_query_vals('SELECT * FROM favorite_ayats') == [(1145, 5354079702)]
