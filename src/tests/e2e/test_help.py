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
import time
from pathlib import Path

import pytest


@pytest.fixture()
def expected_message():
    return '\n'.join([
        'Этот бот поможет тебе изучить Коран по богословскому переводу Шамиля Аляутдинова. ',
        '',
        'Каждое утро, вам будут приходить аяты из Священного Корана.',
        'При нажатии на кнопку Подкасты, вам будут присылаться проповеди с сайта umma.ru.',
        '',
        (
            'Также вы можете отправите номер суры, аята (например 4:7) и получить: аят в оригинале, '
            + 'перевод на русский язык, транслитерацию и аудио'
        ),
    ])


@pytest.fixture()
def load_help_message(db_session):
    db_session.execute(
        (Path(__file__).parent / 'fixtures' / 'admin_messages.sql').read_text(),
    )


@pytest.mark.usefixtures('load_help_message')
def test_help(expected_message, tg_client, bot_name):
    tg_client.send_message(bot_name, '/help')
    for _ in range(50):
        time.sleep(0.1)
        message = next(tg_client.iter_messages(bot_name))
        if message.message != '/help':
            break

    assert message.message == expected_message
