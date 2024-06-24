from typing import Protocol

from pyeo import elegant


@elegant
class AsyncIntOrNone(Protocol):
    """AsyncIntOrNone."""

    async def to_int(self) -> int | None:
        """Числовое представление."""
