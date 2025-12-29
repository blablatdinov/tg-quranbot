# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from integrations.tg.coordinates import Coordinates


@final
@attrs.define(frozen=True)
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
