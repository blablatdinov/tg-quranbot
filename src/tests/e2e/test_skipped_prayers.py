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

import pytest


@pytest.mark.usefixtures('_bot_process')
def test_skipped_prayers(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, '/skipped_prayers')
    messages = wait_until(tg_client, 2)

    assert messages[0].message == '\n'.join([
        'Кол-во непрочитанных намазов:\n',
        'Иртәнге: 0',
        'Өйлә: 4',
        'Икенде: 5',
        'Ахшам: 0',
        'Ястү: 2',
    ])
    assert [
        (button.text, button.data)
        for button_row in messages[0].get_buttons()
        for button in button_row
    ] == [
        ('Иртәнге: (-1)', b'fk'),
        ('Өйлә: (-1)', b'fk'),
        ('Икенде: (-1)', b'fk'),
        ('Ахшам: (-1)', b'fk'),
        ('Ястү: (-1)', b'fk'),
    ]
