# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

import datetime
from pathlib import Path

import httpx
import pytest

from srv.prayers.nt_prayers_text import NtPrayersText
from srv.prayers.fk_prayer_date import FkPrayerDate


@pytest.fixture
def nt_mock(respx_mock):
    respx_mock.get('https://namaz.today/city/kazan').mock(return_value=httpx.Response(
        200,
        text=Path('src/tests/fixtures/nt_response.html').read_text(encoding='utf-8'),
    ))


@pytest.mark.usefixtures('nt_mock')
async def test_today(time_machine):
    time_machine.move_to('2025-01-06')
    got = await NtPrayersText('kazan', FkPrayerDate(datetime.date(2025, 1, 6))).to_str()

    assert got == '\n'.join([
        'Время намаза для г. kazan (06.01.2025)',
        '',
        'Иртәнге: 05:53',
        'Восход: 08:11',
        'Өйлә: 11:50',
        'Икенде: 13:39',
        'Ахшам: 15:28',
        'Ястү: 17:25',
    ])


@pytest.mark.usefixtures('nt_mock')
async def test_by_date():
    got = await NtPrayersText(
        'kazan',
        # TODO #1450:30min Пока возможно получать время намаза только в рамках текущего месяца.
        #  В таблице на странице https://namaz.today/city/kazan приведены данные только на текущий месяц
        #  Оставил коммент с вопросом, пока ждем решения
        FkPrayerDate(datetime.date(2025, 1, 20)),
    ).to_str()

    assert got == '\n'.join([
        'Время намаза для г. kazan (06.01.2025)',
        '',
        'Иртәнге: 05:44',
        'Восход: 07:57',
        'Өйлә: 11:56',
        'Икенде: 14:02',
        'Ахшам: 15:53',
        'Ястү: 17:44',
    ])
