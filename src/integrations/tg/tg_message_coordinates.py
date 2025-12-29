# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from app_types.update import Update
from integrations.tg.coordinates import Coordinates
from integrations.tg.exceptions.update_parse_exceptions import CoordinatesNotFoundError
from services.err_redirect_json_path import ErrRedirectJsonPath
from services.json_path_value import JsonPathValue


@final
@attrs.define(frozen=True)
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
