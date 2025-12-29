# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from integrations.city_name_by_id import CityName
from integrations.tg.coordinates import Coordinates


@final
@attrs.define(frozen=True)
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
        async with httpx.AsyncClient(timeout=5) as http_client:
            response = await http_client.get(url)
        return response.json()['address']['city']
