# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest


@pytest.fixture
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
