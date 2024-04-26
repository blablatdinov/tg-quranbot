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

import pytest


@pytest.fixture()
def expected_message():
    return '\n'.join([
        'Этот бот поможет тебе изучить Коран по богословскому переводу Шамиля Аляутдинова. ',
        '',
        'Каждое утро, вам будут приходить аяты из Священного Корана.',
        'При нажатии на кнопку Подкасты, вам будут присылаться проповеди с сайта umma.ru.',
        '',
        ' '.join([
            'Также вы можете отправите номер суры, аята (например 4:7) и получить: аят в оригинале,',
            'перевод на русский язык, транслитерацию и аудио',
        ]),
    ])


@pytest.mark.usefixtures('_bot_process', '_clear_db')
def test_help(expected_message, tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, '/help')
    messages = wait_until(tg_client, 2)

    assert messages[0].message == expected_message
