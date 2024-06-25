from integrations.tg.coordinates import Coordinates


import attrs
from pyeo import elegant


from typing import final, override


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