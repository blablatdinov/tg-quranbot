import abc

from integrations.client import IntegrationClientInterface
from integrations.schemas import NominatimSearchResponse


class GeoServiceIntegrationInterface(object):
    """Интерфейс интеграции с геосервисом."""

    _request_client: IntegrationClientInterface

    @abc.abstractmethod
    def __init__(self, request_client: IntegrationClientInterface):
        raise NotImplementedError

    @abc.abstractmethod
    async def search(self, latitude: str, longitude: str) -> list[str]:
        """Поиск по координатам.

        :param latitude: str
        :param longitude: str
        :raises NotImplementedError: if not implement
        """
        raise NotImplementedError


class NominatimIntegration(GeoServiceIntegrationInterface):
    """Интеграция с https://nominatim.openstreetmap.org ."""

    _request_client: IntegrationClientInterface

    def __init__(self, request_client: IntegrationClientInterface):
        self._request_client = request_client

    async def search(self, latitude: str, longitude: str) -> list[str]:
        """Поиск по координатам.

        :param latitude: str
        :param longitude: str
        :returns: list[str]
        """
        url_template = 'https://nominatim.openstreetmap.org/reverse.php?lat={latitude}&lon={longitude}&format=jsonv2'
        url = url_template.format(latitude=latitude, longitude=longitude)
        response: NominatimSearchResponse = await self._request_client.act(url, NominatimSearchResponse)
        return response.display_name.replace(',', '').split(' ')
