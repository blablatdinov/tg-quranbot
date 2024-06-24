from app_types.AsyncIntOrNone import AsyncIntOrNone


import attrs
from pyeo import elegant


from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class FkAsyncIntOrNone(AsyncIntOrNone):
    """FkAsyncIntOrNone."""

    _origin_value: int | None

    @override
    async def to_int(self) -> int | None:
        """Числовое представление.

        :return: int | None
        """
        return self._origin_value