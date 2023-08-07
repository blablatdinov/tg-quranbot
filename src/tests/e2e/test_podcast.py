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
def load_podcasts(db_session):
    db_session.execute(
        (Path(__file__).parent / 'fixtures' / 'files.sql').read_text(),
    )
    db_session.execute(
        (Path(__file__).parent / 'fixtures' / 'podcasts.sql').read_text(),
    )
    db_session.execute('SELECT * FROM public.podcasts')
    yield


@pytest.mark.usefixtures('load_podcasts')
def test_podcast(tg_client, bot_name):
    tg_client.send_message(bot_name, '🎧 Подкасты')
    for _ in range(50):
        time.sleep(0.1)
        message = next(tg_client.iter_messages(bot_name))
        if 'http' in message.message:
            break

    assert message.message.startswith('http')
    assert message.message.endswith('.mp3')
