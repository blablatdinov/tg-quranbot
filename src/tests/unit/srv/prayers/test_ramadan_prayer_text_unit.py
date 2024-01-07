"""The MIT License (MIT).

Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

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

from app_types.stringable import FkAsyncStr
from srv.prayers.ramadan_prayer_text import RamadanPrayerText


@pytest.fixture()
def prayer_time_text():
    return '\n'.join([
        'Время намаза для г. Казань (21.10.2023)\n',
        'Иртәнге: 04:22',
        'Восход: 06:26',
        'Өйлә: 12:00',
        'Икенде: 14:35',
        'Ахшам: 16:30',
        'Ястү: 18:12',
    ])


async def test_not_ramadan_mode(prayer_time_text):
    got = await RamadanPrayerText(
        FkAsyncStr(prayer_time_text),
        ramadan_mode=False,
    ).to_str()

    assert got == prayer_time_text


async def test_ramadan_mode(prayer_time_text):
    got = await RamadanPrayerText(
        FkAsyncStr(prayer_time_text),
        ramadan_mode=True,
    ).to_str()

    assert got == '\n'.join([
        'Время намаза для г. Казань (21.10.2023)\n',
        'Иртәнге: 04:22 <i>- Конец сухура</i>',
        'Восход: 06:26',
        'Өйлә: 12:00',
        'Икенде: 14:35',
        'Ахшам: 16:30 <i>- Ифтар</i>',
        'Ястү: 18:12',
    ])
