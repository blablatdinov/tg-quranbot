from pydantic import BaseModel

from integrations.client import IntegrationClientInterface
from integrations.nominatim import NominatimIntegration
from integrations.schemas import NominatimSearchResponse
from settings import settings


class IntegrationClientMock(IntegrationClientInterface):

    async def act(self, url: str, model_for_parse: type(BaseModel)) -> BaseModel:
        path = settings.BASE_DIR / 'tests' / 'fixtures' / 'nominatim_response.json'
        with open(path, 'r') as response_fixture_file:
            return NominatimSearchResponse.parse_raw(response_fixture_file.read())


async def test():
    got = await NominatimIntegration(
        IntegrationClientMock(),
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
