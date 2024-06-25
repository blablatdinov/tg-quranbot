from typing import final, override

import attrs
from pyeo import elegant

from app_types.stringable import SupportsStr


@final
@attrs.define(frozen=True)
@elegant
class ThroughString(SupportsStr):
    """Обертка для строки."""

    _source: str

    @override
    def __str__(self) -> str:
        """Строковое представление.

        :return: str
        """
        return self._source
