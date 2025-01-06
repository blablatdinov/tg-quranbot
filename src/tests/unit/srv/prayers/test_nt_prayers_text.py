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

from pathlib import Path

import httpx
import pytest

from srv.prayers.nt_prayers_text import NtPrayersText


@pytest.fixture
def nt_mock(respx_mock):
    respx_mock.get('https://namaz.today/city/kazan').mock(return_value=httpx.Response(
        200,
        text=Path('src/tests/fixtures/nt_response.html').read_text(encoding='utf-8'),
    ))


@pytest.mark.usefixtures('nt_mock')
async def test():
    got = await NtPrayersText('kazan').to_str()

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


# TODO #1440:30min тест для получения времени намаза по дате
