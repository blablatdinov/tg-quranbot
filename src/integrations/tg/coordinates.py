import re
from typing import Protocol

from app_types.stringable import Stringable
from integrations.tg.exceptions.update_parse_exceptions import CoordinatesNotFoundError


class Coordinates(Protocol):
    """Интерфейс координат."""

    def latitude(self) -> float:
        """Ширина."""

    def longitude(self) -> float:
        """Долгота."""


class TgMessageCoordinates(Coordinates):
    """Координаты, принятые из чата."""

    def __init__(self, raw: Stringable):
        """Конструктор класса.

        :param raw: Stringable
        """
        self._raw = raw

    def latitude(self) -> float:
        """Ширина.

        :return: float
        :raises CoordinatesNotFoundError: если ширина не найдена
        """
        regex_result = re.search(r'latitude"(:|: )((-|)\d+\.\d+)', str(self._raw))
        if not regex_result:
            raise CoordinatesNotFoundError
        return float(regex_result.group(2))

    def longitude(self) -> float:
        """Долгота.

        :return: float
        :raises CoordinatesNotFoundError: если долгота не найдена
        """
        regex_result = re.search(r'longitude"(:|: )((-|)\d+\.\d+)', str(self._raw))
        if not regex_result:
            raise CoordinatesNotFoundError
        return float(regex_result.group(2))
