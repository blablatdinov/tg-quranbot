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
import datetime
import time

import httpx
import pytest


@pytest.fixture()
def user_city(tg_client, db_conn, bot_name):
    tg_client.send_message(bot_name, '/start')
    time.sleep(10)
    db_cursor = db_conn.cursor()
    db_cursor.execute(
        'UPDATE users SET city_id = %s WHERE chat_id = %s',
        ('bc932b25-707e-4af1-8b6e-facb5e6dfa9b', 5354079702),
    )
    db_conn.commit()


@pytest.fixture()
def expected_message():
    dumrt_response = httpx.get(
        'http://dumrt.ru/netcat_files/482/640/Kazan.csv?t={0}'.format(datetime.datetime.now().strftime('%d%m%y')),
    ).text
    for line in dumrt_response.strip().split('\n'):
        elems = line.strip().split(';')
        if datetime.datetime.now().strftime('%d.%m.%Y') == elems[0]:
            return '\n'.join([
                'Время намаза для г. Казань ({0})'.format(datetime.datetime.now().strftime('%d.%m.%Y')),
                '',
                'Иртәнге: {0}'.format(datetime.datetime.strptime(elems[1], '%H:%M').strftime('%H:%M')),
                'Восход: {0}'.format(datetime.datetime.strptime(elems[3], '%H:%M').strftime('%H:%M')),
                'Өйлә: {0}'.format(datetime.datetime.strptime(elems[5], '%H:%M').strftime('%H:%M')),
                'Икенде: {0}'.format(datetime.datetime.strptime(elems[6], '%H:%M').strftime('%H:%M')),
                'Ахшам: {0}'.format(datetime.datetime.strptime(elems[7], '%H:%M').strftime('%H:%M')),
                'Ястү: {0}'.format(datetime.datetime.strptime(elems[8], '%H:%M').strftime('%H:%M')),
            ])


@pytest.mark.usefixtures('bot_process', 'clear_db', 'user_city')
def test_prayer_times(tg_client, bot_name, expected_message):
    tg_client.send_message(bot_name, 'Время намаза')
    for _ in range(50):
        time.sleep(0.1)
        messages = [mess.message for mess in tg_client.iter_messages(bot_name) if mess.message]
        if len(messages) == 5:
            break

    assert messages[0] == expected_message