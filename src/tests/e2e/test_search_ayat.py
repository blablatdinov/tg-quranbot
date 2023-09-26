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


@pytest.mark.parametrize(('query', 'expected'), [
    ('8:7', 'src/tests/e2e/fixtures/8_7_ayat.txt'),
    ('2:1', 'src/tests/e2e/fixtures/2_1_ayat.txt'),
    ('2:3', 'src/tests/e2e/fixtures/2_1_ayat.txt'),
])
@pytest.mark.usefixtures('_bot_process', '_clear_db')
def test_search_by_sura_ayat(tg_client, bot_name, query, expected, wait_until):
    tg_client.send_message(bot_name, query)
    last_messages = wait_until(tg_client, 3)

    assert last_messages[1].message == Path(expected).read_text()


@pytest.mark.usefixtures('_bot_process', '_clear_db')
def test_paginate_in_search_by_sura_ayat(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, '8:7')
    last_messages = wait_until(tg_client, 3)
    next(
        button
        for button_row in last_messages[1].get_buttons()
        for button in button_row
        if button.text == '8:8 ->'
    ).click()
    last_messages = wait_until(tg_client, 5)

    assert last_messages[1].message == Path('src/tests/e2e/fixtures/8_8_ayat.txt').read_text()


@pytest.mark.usefixtures('_bot_process', '_clear_db')
def test_by_word(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, 'Найти аят')
    wait_until(tg_client, 2)
    tg_client.send_message(bot_name, 'камни')
    last_messages = wait_until(tg_client, 5)

    assert last_messages[1].message == Path('src/tests/e2e/fixtures/2_24_ayat.txt').read_text()
    assert last_messages[0].message == 'https://umma.ru/audio/Ozvucjka-statei/Quran/audio/Husary_64/2/002024.mp3'
    assert [
        (button.text, button.data)
        for button_row in last_messages[1].get_buttons()
        for button in button_row
    ] == [
        ('стр. 1/5', b'fake'),
        ('11:83 ->', b'getSAyat(1533)'),
        ('Добавить в избранное', b'addToFavor(17)'),
    ]


@pytest.mark.usefixtures('_bot_process', '_clear_db')
def test_search_pagination_forward(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, 'Найти аят')
    wait_until(tg_client, 2)
    tg_client.send_message(bot_name, 'камни')
    last_messages = wait_until(tg_client, 5)
    next(
        button
        for button_row in last_messages[1].get_buttons()
        for button in button_row
        if button.text == '11:83 ->'
    ).click()
    last_messages = wait_until(tg_client, 7)

    assert last_messages[1].message == Path('src/tests/e2e/fixtures/11_83_ayat.txt').read_text()
    assert last_messages[0].message == 'https://umma.ru/audio/Ozvucjka-statei/Quran/audio/Husary_64/11/011083.mp3'


@pytest.mark.usefixtures('_bot_process', '_clear_db')
def test_search_pagination_backward(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, 'Найти аят')
    wait_until(tg_client, 2)
    tg_client.send_message(bot_name, 'камни')
    last_messages = wait_until(tg_client, 5)
    next(
        button
        for button_row in last_messages[1].get_buttons()
        for button in button_row
        if button.text == '11:83 ->'
    ).click()
    last_messages = wait_until(tg_client, 7)
    next(
        button
        for button_row in last_messages[1].get_buttons()
        for button in button_row
        if button.text == '<- 2:24'
    ).click()
    last_messages = wait_until(tg_client, 9)

    assert last_messages[1].message == Path('src/tests/e2e/fixtures/2_24_ayat.txt').read_text()


@pytest.mark.usefixtures('_bot_process', '_clear_db')
def test_add_to_favor_from_search(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, '/start')
    wait_until(tg_client, 3)
    tg_client.send_message(bot_name, 'Найти аят')
    wait_until(tg_client, 5)
    tg_client.send_message(bot_name, 'камни')
    last_messages = wait_until(tg_client, 8)
    next(
        button
        for button_row in last_messages[1].get_buttons()
        for button in button_row
        if button.text == 'Добавить в избранное'
    ).click()
    last_messages = wait_until(tg_client, 8)

    assert last_messages[1].message == Path('src/tests/e2e/fixtures/2_24_ayat.txt').read_text()
    assert [
        (button.text, button.data)
        for button_row in last_messages[1].get_buttons()
        for button in button_row
    ] == [
        ('стр. 1/5', b'fake'),
        ('11:83 ->', b'getSAyat(1533)'),
        ('Удалить из избранного', b'removeFromFavor(17)'),
    ]
