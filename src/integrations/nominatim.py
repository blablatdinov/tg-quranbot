"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

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
from typing import Protocol, final

from integrations.client import IntegrationClientInterface
from integrations.schemas import NominatimSearchResponse


class GeoServiceIntegrationInterface(Protocol):
    """Интерфейс интеграции с геосервисом."""

    async def search(self, latitude: str, longitude: str) -> str:
        """Поиск по координатам.

        :param latitude: str
        :param longitude: str
        """


@final
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
