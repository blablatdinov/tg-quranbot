from typing import Protocol

from pyeo import elegant


@elegant
class AsyncSupportsStr(Protocol):
    """Интерфейс объектов, которые можно привести к строке."""

    async def to_str(self) -> str:
        """Приведение к строке."""
