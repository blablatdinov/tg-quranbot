from pydantic import BaseModel

from integrations.client import IntegrationClientInterface
from integrations.nominatim import NominatimIntegration
from integrations.schemas import NominatimSearchResponse


class IntegrationClientMock(IntegrationClientInterface):

    async def act(self, url: str, model_for_parse: type(BaseModel)) -> BaseModel:
        return NominatimSearchResponse.parse_raw("""
        {
            "place_id": 138531976,
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright",
            "osm_type": "way",
            "osm_id": 158473506,
            "lat": "55.76687415",
            "lon": "49.10060765",
            "place_rank": 30,
            "category": "building",
            "type": "yes",
            "importance": 0,
            "addresstype": "building",
            "name": null,
            "display_name": "44, улица Меховщиков, Ново-Татарская слобода, Вахитовский район, Казань, городской округ Казань, Татарстан, Приволжский федеральный округ, 420108, Россия",
            "address": {
                "house_number": "44",
                "road": "улица Меховщиков",
                "suburb": "Ново-Татарская слобода",
                "city_district": "Вахитовский район",
                "city": "Казань",
                "county": "городской округ Казань",
                "state": "Татарстан",
                "ISO3166-2-lvl4": "RU-TA",
                "region": "Приволжский федеральный округ",
                "postcode": "420108",
                "country": "Россия",
                "country_code": "ru"
            },
            "boundingbox": [
                "55.766663",
                "55.7670853",
                "49.1004085",
                "49.1008068"
            ]
        }
        """)


async def test():
    got = await NominatimIntegration(
        IntegrationClientMock()
    ).search('55.76728145852831', '49.100915750000006')

    assert got == [
        '44',
        'улица',
        'Меховщиков',
        'Ново-Татарская',
        'слобода',
        'Вахитовский',
        'район',
        'Казань',
        'городской',
        'округ',
        'Казань',
        'Татарстан',
        'Приволжский',
        'федеральный',
        'округ',
        '420108',
        'Россия',
    ]
