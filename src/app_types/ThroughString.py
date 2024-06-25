from app_types.stringable import SupportsStr


import attrs
from pyeo import elegant


from typing import final, override


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