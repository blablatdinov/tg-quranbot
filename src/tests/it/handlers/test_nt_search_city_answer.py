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

import httpx
import pytest
import ujson

from app_types.fk_update import FkUpdate
from handlers.nt_search_city_answer import NtSearchCityAnswer
from srv.prayers.fk_city import FkCity


@pytest.fixture
def nt_mock(respx_mock):
    respx_mock.get('https://namaz.today/city.php?term=Казань').mock(
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


# TODO #1428:30min Написать парсер тест для класса NtSearchCityAnswer.
@pytest.mark.usefixtures('nt_mock')
async def test():
    got = await NtSearchCityAnswer().build(
        FkUpdate(ujson.dumps({
            'message': {'text': 'Казань'},
            'chat': {'id': 384957},
        })),
    )

    assert got == [FkCity('', 'Казань')]
