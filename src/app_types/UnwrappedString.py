from typing import final, override

import attrs
from pyeo import elegant

from app_types.stringable import SupportsStr


@final
@attrs.define(frozen=True)
@elegant
class UnwrappedString(SupportsStr):
    """Строки без переноса."""

    _origin: SupportsStr

    @override
    def __str__(self) -> str:
        """Строковое представление.

        :return: str
        """
        return str(self._origin).replace('\n', '')
