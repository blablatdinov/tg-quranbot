from integrations.city_name_by_id import CityName
from integrations.tg.coordinates import Coordinates


import attrs
import httpx
from pyeo import elegant


from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class NominatimCityName(CityName):
    """Интеграция с https://nominatim.openstreetmap.org ."""

    _coordinates: Coordinates

    @override
    async def to_str(self) -> str:
        """Поиск по координатам.

        curl https://nominatim.openstreetmap.org/reverse.php?lat=55.7887&lon=49.1221&format=jsonv2

        :returns: CityName
        """
        url_template = 'https://nominatim.openstreetmap.org/reverse.php?lat={latitude}&lon={longitude}&format=jsonv2'
        url = url_template.format(
            latitude=self._coordinates.latitude(),
            longitude=self._coordinates.longitude(),
        )
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(url)
        return response.json()['address']['city']