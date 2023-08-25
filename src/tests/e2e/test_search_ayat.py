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


@pytest.mark.parametrize('query,expected', [
    ('8:7', 'src/tests/e2e/fixtures/8_7_ayat.txt'),
    ('2:1', 'src/tests/e2e/fixtures/2_1_ayat.txt'),
    ('2:3', 'src/tests/e2e/fixtures/2_1_ayat.txt'),
])
@pytest.mark.usefixtures('bot_process', 'clear_db')
def test_search_by_sura_ayat(tg_client, bot_name, query, expected):
    tg_client.send_message(bot_name, query)
    for _ in range(50):
        time.sleep(0.1)
        last_messages = [x for x in tg_client.iter_messages(bot_name)][::-1][1:]
        if len(last_messages) == 3:
            break

    assert last_messages[1].message == Path(expected).read_text()
