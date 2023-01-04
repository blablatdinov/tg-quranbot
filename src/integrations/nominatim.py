from typing import Protocol

from integrations.client import IntegrationClientInterface
from integrations.schemas import NominatimSearchResponse


class GeoServiceIntegrationInterface(Protocol):
    """Интерфейс интеграции с геосервисом."""

    async def search(self, latitude: str, longitude: str) -> str:
        """Поиск по координатам.

        :param latitude: str
        :param longitude: str
        """


class NominatimIntegration(GeoServiceIntegrationInterface):
    """Интеграция с https://nominatim.openstreetmap.org ."""

    _request_client: IntegrationClientInterface

    def __init__(self, request_client: IntegrationClientInterface):
        """Конструктор класса.

        :param request_client: IntegrationClientInterface
        """
        self._request_client = request_client

    async def search(self, latitude: str, longitude: str) -> str:
        """Поиск по координатам.

        :param latitude: str
        :param longitude: str
        :returns: list[str]
        """
        url_template = 'https://nominatim.openstreetmap.org/reverse.php?lat={latitude}&lon={longitude}&format=jsonv2'
        url = url_template.format(latitude=latitude, longitude=longitude)
        response: NominatimSearchResponse = await self._request_client.act(url, NominatimSearchResponse)
        return response.address.city
