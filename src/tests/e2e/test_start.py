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
            'Также вы можете отправите номер суры, аята (например 4:7) и получить: аят в оригинале, перевод на '
            + 'русский язык, транслитерацию и аудио'
        ),
    ])


@pytest.fixture()
def start_message(db_session):
    for name in 'suras.sql', 'files.sql', 'ayats.sql', 'admin_messages.sql':
        db_session.execute(
            (Path(__file__).parent / 'fixtures' / name).read_text(),
        )

@pytest.fixture()
def expected_ayat():
    return '\n'.join([
        '1:1-7)',
        ''
        'بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ١ الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ٢ الرَّحْمَنِ الرَّحِيمِ٣ مَالِكِ يَوْمِ الدِّينِ٤ إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ٥ اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ٦ صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ٧',
        '',
        'Именем Аллаха [именем Бога, Творца всего сущего, Одного и Единственного для всех и вся], милость Которого вечна и безгранична. Истинное восхваление принадлежит только Аллаху, Господу миров, милость Которого вечна и безгранична, Владыке Судного Дня. Тебе поклоняемся и у Тебя просим помощи [поддержки, Божьего благословения в делах наших]. Направь нас на правильный путь. Путь тех, которым он был дарован [из числа пророков и посланников, праведников и мучеников, а также всех тех, кто удостоен был такой чести — идти правильным путем]. Не тех, на которых Ты разгневался, и не тех, которые сошли с него[,] .',
        '',
        '[Бисмилляяхир-Рахмаанир-Рахиим (1) Аль-Хамду Лилляяхи Раббиль-`Алямиин(2) Эр-Рахмаанир-Рахимм (3) Малики йаумид-диин (4) Ийяякя ня`буду уа ийяякя наста`иин (5) Ихдиня ссырааталь-мустакыыйм (6) Ссырааталь-лязиина ан`амта `алейхим, гайриль-магдууби `алейхим уа ляд-дааалиин. (7)]',
    ])


def test_start(expected_message, tg_client, bot_name, start_message, expected_ayat):
    tg_client.send_message(bot_name, '/start')
    for _ in range(50):
        time.sleep(0.1)
        last_messages = [x for x in tg_client.iter_messages(bot_name)][::-1][1:]
        if len(last_messages) == 3:
            break

    assert last_messages[1].message == expected_message
    assert last_messages[2].message == expected_ayat
