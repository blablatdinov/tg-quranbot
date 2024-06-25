from typing import final, override

import attrs
from pyeo import elegant

from integrations.tg.coordinates import Coordinates


@final
@attrs.define(frozen=True)
@elegant
class FkCoordinates(Coordinates):
    """Стаб для координат."""

    _latitude: float
    _longitude: float

    @override
    def latitude(self) -> float:
        """Широта.

        :return: float
        """
        return self._latitude

    @override
    def longitude(self) -> float:
        """Долгота.

        :return: float
        """
        return self._longitude
