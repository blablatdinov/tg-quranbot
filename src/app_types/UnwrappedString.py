from app_types.stringable import SupportsStr


import attrs
from pyeo import elegant


from typing import final, override


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