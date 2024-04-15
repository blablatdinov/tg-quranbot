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

import httpx
import pytest
import ujson

from app_types.logger import FkLogSink
from app_types.update import FkUpdate
from handlers.search_city_answer import SearchCityAnswer
from integrations.tg.tg_answers import FkAnswer


@pytest.fixture()
def _mock_nominatim(respx_mock):
    respx_mock.get(
        'https://nominatim.openstreetmap.org/reverse.php?lat=55.7887&lon=49.1221&format=jsonv2',
    ).mock(
        return_value=httpx.Response(
            200,
            text=ujson.dumps({
                'address': {
                    'ISO3166-2-lvl4': 'RU-TA',
                    'city': 'Казань',
                    'city_district': 'Вахитовский район',
                    'country': 'Россия',
                    'country_code': 'ru',
                    'county': 'городской округ Казань',
                    'house_number': '12',
                    'postcode': '420111',
                    'region': 'Приволжский федеральный округ',
                    'road': 'Университетская улица',
                    'state': 'Татарстан',
                    'suburb': 'Старо-Татарская слобода',
                },
                'addresstype': 'building',
                'boundingbox': ['55.7886681', '55.7889864', '49.1218618', '49.1223806'],
                'category': 'building',
                'display_name': ' '.join([
                    '12, Университетская улица, Старо-Татарская слобода,',
                    'Вахитовский район, Казань, городской округ Казань,',
                    'Татарстан, Приволжский федеральный округ, 420111, Россия',
                ]),
                'importance': 9.9,
                'lat': '55.7888272',
                'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright',
                'lon': '49.12212116815689',
                'name': '',
                'osm_id': 105336438,
                'osm_type': 'way',
                'place_id': 128743364,
                'place_rank': 30,
                'type': 'apartments',
            }),
        )
    )


async def test_message(pgsql, fake_redis):
    debug = False
    got = await SearchCityAnswer(pgsql, FkAnswer(), debug, fake_redis, FkLogSink()).build(
        FkUpdate(
            ujson.dumps({
                'message': {'text': 'Kazan'},
                'chat': {'id': 384957},
            })
        ),
    )

    assert got[0].url.params['text'] == 'Этот город не поддерживается'


@pytest.mark.usefixtures('_mock_nominatim')
async def test_location(pgsql, fake_redis):
    debug = False
    got = await SearchCityAnswer(pgsql, FkAnswer(), debug, fake_redis, FkLogSink()).build(
        FkUpdate(
            ujson.dumps({
                'chat': {'id': 34847935},
                'latitude': 55.7887,
                'longitude': 49.1221,
            })
        ),
    )

    assert got[0].url.params['text'] == 'Этот город не поддерживается'
