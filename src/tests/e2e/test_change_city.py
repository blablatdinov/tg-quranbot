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
import pytest
from telethon.sync import TelegramClient


@pytest.fixture()
def _user_city(tg_client, db_conn, bot_name, wait_until):
    tg_client.send_message(bot_name, '/start')
    wait_until(tg_client, 3)
    db_cursor = db_conn.cursor()
    db_cursor.execute(
        'UPDATE users SET city_id = %s WHERE chat_id = %s',
        ('bc932b25-707e-4af1-8b6e-facb5e6dfa9b', 5354079702),
    )
    db_conn.commit()


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_user_city')
def test_change_city_by_name(tg_client, bot_name, wait_until, db_query_vals):
    tg_client.send_message(bot_name, 'Поменять город')
    wait_until(tg_client, 5)
    tg_client.send_message(bot_name, 'Набережные Челны')
    messages = wait_until(tg_client, 7)

    assert messages[0].message == 'Вам будет приходить время намаза для города Набережные Челны'
    assert db_query_vals('SELECT city_id FROM users WHERE chat_id = 5354079702') == [
        ('bd92bb55-10ba-4095-9a3e-c7c5737a354b',),
    ]


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_user_city')
@pytest.mark.flaky(retries=3)
def test_change_city_by_search(tg_client: TelegramClient, bot_name, wait_until, db_query_vals):
    tg_client.send_message(bot_name, 'Поменять город')
    messages = wait_until(tg_client, 5)
    buttons = [
        button.text
        for button_row in messages[0].get_buttons()
        for button in button_row
    ]
    cities = tg_client.inline_query(bot_name, 'Набережные')
    cities[0].click(bot_name)
    messages = wait_until(tg_client, 7)

    assert buttons == ['Поиск города']
    assert messages[0].message == 'Вам будет приходить время намаза для города Набережные Челны'
    assert db_query_vals('SELECT city_id FROM users WHERE chat_id = 5354079702') == [
        ('bd92bb55-10ba-4095-9a3e-c7c5737a354b',),
    ]


@pytest.mark.usefixtures('_bot_process', '_clear_db')
def test_not_registred(tg_client, bot_name, wait_until, db_query_vals):
    tg_client.send_message(bot_name, 'Поменять город')
    wait_until(tg_client, 2)
    tg_client.send_message(bot_name, 'Набережные Челны')
    messages = wait_until(tg_client, 4)

    assert messages[0].message == 'Вам будет приходить время намаза для города Набережные Челны'
    assert db_query_vals('SELECT city_id FROM users WHERE chat_id = 5354079702') == [
        ('bd92bb55-10ba-4095-9a3e-c7c5737a354b',),
    ]
