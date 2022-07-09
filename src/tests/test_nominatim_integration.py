from integrations.nominatim import NominatimIntegration
from settings import settings
from tests.mocks.integration_client import IntegrationClientMock


async def test():
    got = await NominatimIntegration(
        IntegrationClientMock(settings.BASE_DIR / 'tests' / 'fixtures' / 'nominatim_response_kazan.json'),
    ).search('55.76728145852831', '49.100915750000006')

    assert got == 'Казань'
