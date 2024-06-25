from app_types.update import Update
from integrations.tg.coordinates import Coordinates
from integrations.tg.exceptions.update_parse_exceptions import CoordinatesNotFoundError
from services.ErrRedirectJsonPath import ErrRedirectJsonPath
from services.JsonPathValue import JsonPathValue


import attrs
from pyeo import elegant


from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class TgMessageCoordinates(Coordinates):
    """Координаты, принятые из чата."""

    _update: Update

    @override
    def latitude(self) -> float:
        """Ширина.

        :return: float
        """
        return float(
            ErrRedirectJsonPath(
                JsonPathValue(
                    self._update.asdict(),
                    '$..[latitude]',
                ),
                CoordinatesNotFoundError(),
            ).evaluate(),
        )

    @override
    def longitude(self) -> float:
        """Долгота.

        :return: float
        """
        return float(
            ErrRedirectJsonPath(
                JsonPathValue(
                    self._update.asdict(),
                    '$..[longitude]',
                ),
                CoordinatesNotFoundError(),
            ).evaluate(),
        )