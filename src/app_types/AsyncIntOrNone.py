from pyeo import elegant


from typing import Protocol


@elegant
class AsyncIntOrNone(Protocol):
    """AsyncIntOrNone."""

    async def to_int(self) -> int | None:
        """Числовое представление."""