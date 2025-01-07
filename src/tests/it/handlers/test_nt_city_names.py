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

# TODO #1443:30min Перенести файл в unit тесты
#  city_names не относится к handlers

import httpx
import pytest
import ujson

from handlers.nt_city_names import NtCityNames


@pytest.fixture
def nt_mock(respx_mock):
    respx_mock.get('https://namaz.today/city.php?term=Каза').mock(
        return_value=httpx.Response(
            status_code=200,
            text=ujson.dumps([{
                'ID': '125',
                'value': ' '.join([
                    '<span class="city-1-item">Казань</span>',
                    '» <span class="city-2-item">Республика Татарстан</span>',
                    '» <span class="city-1-item">Россия</span>',
                ]),
                'url': 'https://namaz.today/city/kazan',
                'city': 'Казань',
            }]),
        ),
    )


@pytest.fixture
def nt_mock_empty(respx_mock):
    respx_mock.get('https://namaz.today/city.php?term=8$@90').mock(
        return_value=httpx.Response(
            status_code=200,
            text='[]',
        ),
    )


@pytest.mark.usefixtures('nt_mock')
async def test():
    got = await NtCityNames(
        'Каза',
    ).to_list()

    assert got == ['Казань']


@pytest.mark.usefixtures('nt_mock_empty')
async def test_empty_list():
    got = await NtCityNames(
        '8$@90',
    ).to_list()

    assert got == []
